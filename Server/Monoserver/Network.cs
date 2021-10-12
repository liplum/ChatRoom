using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Protocols;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Diagnostics.CodeAnalysis;
using System.Net;
using System.Net.Sockets;
using IServiceProvider = ChattingRoom.Core.IServiceProvider;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private class Network : INetwork
    {
        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, (IConnection connection, Thread listning)> _allConnections = new();
        private TcpListener? _serverSocket;
        private readonly object _lock = new();
        private ILogger? Logger
        {
            get; set;
        }

        private Monoserver Outer
        {
            get; init;
        }
        public Network(Monoserver outer)
        {
            Outer = outer;
        }

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {
            if (_allConnections.TryGetValue(token, out var info))
            {
                var connection = info.connection;
                connection.Send(datapack);
            }
        }

        public void RecevieDatapack([NotNull] IDatapack datapack)
        {
            var jsonString = Utils.ConvertToStringWithLengthStartingUnicode(datapack.ToBytes());
            dynamic json = JObject.Parse(jsonString);
            string? channelName = json.ChannalName;
            int? messageID = json.MessageID;
            string content = json.Content ?? "";
            if (channelName is not null &&
                messageID is not null &&
                _allChannels.TryGetValue(channelName, out var channel))
            {
                channel.ReceiveMessage(messageID.Value, content);
            }
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            Logger = serviceProvider.Reslove<ILogger>();
        }

        private readonly UnicodeBytesConverter _unicoder = new();

        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
            var json = new JObject();
            msg.Deserialize(json);
            string jsonTxt = json.ToString(Formatting.None);
            var stringBytes = _unicoder.ConvertToBytes(jsonTxt, false);
            var datapack = new WriteableDatapack();
            datapack.Write(stringBytes.Length).Write(stringBytes);
            SendDatapackTo(datapack, target);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            foreach (var token in _allConnections.Keys)
            {
                SendMessage(token, msg);
            }
        }

        public IMessageChannel New(string channelName)
        {
            return new MessageChannel(this, Outer, channelName);
        }

        private Thread? _listen;

        public void StartService()
        {
            Logger!.SendMessage("Network component is preparing to start.");
            _serverSocket = new TcpListener(IPAddress.Any, Protocol.Connection.Port);
            _serverSocket.Start();
            Logger!.SendMessage("Network component started.");
            _listen = new Thread(() =>
            {
                while (true)
                {
                    var client = _serverSocket.AcceptTcpClient();
                    if (client.Client.RemoteEndPoint is IPEndPoint ipEndPoint)
                    {
                        var ip = ipEndPoint.Address;
                        var token = new NetworkToken(ip);
                        Logger!.SendWarn($"{ip} connected.");
                        AddNewClient(token, client);
                    }
                }
            });
            _listen.Start();
            Logger!.SendMessage("Server started listening connection of clients.");
        }

        private void AddNewClient([NotNull] NetworkToken token, [NotNull] TcpClient client)
        {
            var listeningThread = new Thread(() =>
            {
                using var stream = client.GetStream();
                while (true)
                {
                    if (!client.Connected)
                    {
                        break;
                    }
                    var datapack = Datapack.ReadOne(stream);
                    if (!datapack.IsEmpty)
                    {
                        RecevieDatapack(datapack);
                    }
                }

                RemoveClient(token, () =>
                {
                    if (client.Connected)
                    {
                        client.Client.Shutdown(SocketShutdown.Both);
                        Logger!.SendWarn($"{token.IpAddress} disconnected.");
                    }
                });
            });

            lock (_lock)
            {
                _allConnections[token] = (new SocketConnection(this, token, client), listeningThread);
            }

            listeningThread.Start();
        }

        private void RemoveClient([NotNull] NetworkToken token, Action? afterRemoved = null)
        {
            lock (_lock)
            {
                _allConnections.Remove(token);
            }
            afterRemoved?.Invoke();
        }

        public void StopService()
        {
            Logger!.SendMessage("Network component is preparing to stop.");
            _listen?.Interrupt();
            Logger!.SendMessage("Network component stoped.");
        }
    }

    private class MessageChannel : IMessageChannel
    {
        public Network Outer
        {
            get; init;
        }
        public Monoserver Server
        {
            get; init;
        }

        public MessageChannel([NotNull] Network outer, Monoserver server, [NotNull] string channelName)
        {
            Outer = outer;
            Server = server;
            ChannelName = channelName;
        }

        public string ChannelName
        {
            get; init;
        }

        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
            Outer.SendMessage(target, msg);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            Outer.SendMessageToAll(msg);
        }

        private readonly Dictionary<int, (Type msg, dynamic handler)> _Id2MsgTypeAndHandler = new();

        public void RegisterMessageType<MessageType, HandlerType>(int messageID)
            where MessageType : class, IMessage, new()
            where HandlerType : class, IMessageHandler<MessageType>, new()
        {
            _Id2MsgTypeAndHandler[messageID] = (typeof(MessageType), new HandlerType());
        }

        public void ReceiveMessage(int messageID, dynamic jsonContent)
        {
            if (_Id2MsgTypeAndHandler.TryGetValue(messageID, out var info))
            {
                dynamic? msg = Activator.CreateInstance(info.msg);
                if (msg is not null)
                {
                    msg.Deserialize(jsonContent);
                    var hanlder = info.handler;
                    hanlder.Handle(msg, Server);
                }
            }
        }
    }
    private class SocketConnection : IConnection
    {
        public NetworkStream Stream
        {
            get; private set;
        }
        public TcpClient TcpClient
        {
            get; private set;
        }

        public Socket Socket
        {
            get; private set;
        }

        private Network Outer
        {
            get; init;
        }

        private bool Terminaled { get; set; }

        public bool Terminal()
        {
            if (Terminaled)
            {
                return false;
            }
            Disconnect();
            Terminaled = true;
            Socket.Close();
            return true;
        }

        private NetworkToken Token
        {
            get; init;
        }

        public SocketConnection(Network outer, NetworkToken token, TcpClient tcpClient)
        {
            Outer = outer;
            Token = token;
            TcpClient = tcpClient;
            Socket = tcpClient.Client;
            Stream = tcpClient.GetStream();
        }

        public bool IsConnected
        {
            get; private set;
        }

        public bool Connect()
        {
            if (IsConnected)
            {
                return false;
            }
            IsConnected = true;
            return true;
        }

        public bool Disconnect()
        {
            if (!IsConnected)
            {
                return false;
            }
            IsConnected = false;
            return true;
        }

        public void Send([NotNull] IDatapack datapack)
        {
            if (!IsConnected)
            {
                throw new ConnectionClosedException();
            }
            if (Stream.CanWrite)
            {
                datapack.WriteInto(Stream);
            }
        }
    }
}
