using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Networks;
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

        public Monoserver Server
        {
            get; init;
        }
        public Network(Monoserver server)
        {
            Server = server;
        }

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {
            if (_allConnections.TryGetValue(token, out var info))
            {
                var connection = info.connection;
                connection.Send(datapack);
            }
        }

        public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null)
        {
            var jsonString = Utils.ConvertToStringWithLengthStartingUnicode(datapack.ToBytes());
            dynamic json = JObject.Parse(jsonString);
            string? channelName = json.ChannalName;
            string? messageID = json.MessageID;
            string content = json.Content ?? "";
            if (channelName is not null &&
                messageID is not null &&
                _allChannels.TryGetValue(channelName, out var channel))
            {
                channel.ReceiveMessage(messageID, content, token);
            }
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            Logger = serviceProvider.Reslove<ILogger>();
        }

        private readonly UnicodeBytesConverter _unicoder = new();

        public void SendMessage([NotNull] IMessageChannel channel, [NotNull] NetworkToken target, [NotNull] IMessage msg, string msgID)
        {
            dynamic json = new JObject();
            WriteHeader();
            json.Content = new JObject();
            msg.Serialize(json.Content);
            string jsonTxt = json.ToString(Formatting.None);
            var stringBytes = _unicoder.ConvertToBytes(jsonTxt);
            var datapack = new WriteableDatapack();
            datapack.Write(stringBytes.Length)
                .Write(stringBytes);
            SendDatapackTo(datapack, target);

            void WriteHeader()
            {
                json.ChannalName = channel.ChannelName;
                json.MessageID = msgID;
            }
        }

        public void SendMessageToAll([NotNull] IMessageChannel channel, [NotNull] IMessage msg, string msgID)
        {
            foreach (var token in _allConnections.Keys)
            {
                SendMessage(channel, token, msg, msgID);
            }
        }

        public IMessageChannel New(string channelName)
        {
            return new MessageChannel(this, channelName);
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
            var connection = new SocketConnection(this, token, client);
            connection.Connect();
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
                        RecevieDatapack(datapack, token);
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
                _allConnections[token] = (connection, listeningThread);
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
            foreach (var pair in _allConnections.Values)
            {
                var c = pair.connection;
                c.Terminal();
            }
            Logger!.SendMessage("Network component stoped.");
        }
    }

    private class MessageChannel : IMessageChannel
    {
        public Network Network
        {
            get; init;
        }

        public MessageChannel([NotNull] Network network, [NotNull] string channelName)
        {
            Network = network;
            ChannelName = channelName;
        }

        public string ChannelName
        {
            get; init;
        }

        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
            Network.SendMessage(this, target, msg, _msg2Id[msg.GetType()]);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            Network.SendMessageToAll(this, msg, _msg2Id[msg.GetType()]);
        }

        private readonly Dictionary<string, (Type msg, dynamic? handler)> _id2MsgTypeAndHandler = new();
        private readonly Dictionary<Type, string> _msg2Id = new();

        public void RegisterMessageHandler<Msg, Handler>(string messageID)
            where Msg : class, IMessage, new()
            where Handler : class, IMessageHandler<Msg>, new()
        {
            var msg = typeof(Msg);
            _msg2Id[msg] = messageID;
            _id2MsgTypeAndHandler[messageID] = (msg, new Handler());
        }

        public void RegisterMessage<Msg>(string messageID) where Msg : class, IMessage, new()
        {
            var msg = typeof(Msg);
            _msg2Id[msg] = messageID;
            _id2MsgTypeAndHandler[messageID] = (msg, null);
        }

        public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null)
        {
            if (_id2MsgTypeAndHandler.TryGetValue(messageID, out var info))
            {
                dynamic? msg = Activator.CreateInstance(info.msg);
                if (msg is not null)
                {
                    msg.Deserialize(jsonContent);
                    var hanlder = info.handler;
                    if (hanlder is not null)
                    {
                        var context = new MessageContext(Network.Server, this)
                        {
                            ClientToken = token
                        };
                        hanlder.Handle(msg, context);
                    }
                }
            }
        }

        public bool RegisterUser(int UserID)
        {
            throw new NotImplementedException();
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

        public Network Outer
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
