using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Utils;
using ChattingRoom.Server.Protocols;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Diagnostics.CodeAnalysis;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using IServiceProvider = ChattingRoom.Core.IServiceProvider;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private class Network : INetwork
    {
        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, (IConnection connection, Thread listning)> _allConnections = new();
        private TcpListener? _serverSocket;
        private readonly object _clientLock = new();
        private readonly object _channelLock = new();
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
        private int _buffSize = 1024;
        public int BufferSize
        {
            get => _buffSize;
            set
            {
                if (value <= 0)
                    throw new ArgumentOutOfRangeException(nameof(BufferSize));
                _buffSize = value;
            }
        }

        #region Event
        public event OnClientConnectedHandler? OnClientConnected;
        #endregion

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {
            lock (_clientLock)
            {
                if (_allConnections.TryGetValue(token, out var info))
                {
                    var connection = info.connection;
                    connection.Send(datapack);
                }
            }
        }
        private static readonly string EmptyJObjectStr = new JObject().ToString();
        public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null)
        {
            var jsonString = _unicoder.ConvertToString(datapack.ToBytes());
            try
            {
                dynamic json = JObject.Parse(jsonString);
                string? channelName = json.ChannalName;
                string? messageID = json.MessageID;
                string content = json.Content ?? EmptyJObjectStr;
                lock (_channelLock)
                {
                    if ((channelName, messageID).NotNull() &&
                        _allChannels.TryGetValue(channelName, out var channel))
                    {
                        channel.ReceiveMessage(messageID, content, token);
                    }
                }
            }
            catch
            {
                Logger!.SendError($"Cannot analyse datapack:{jsonString}");
            }
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            Logger = serviceProvider.Reslove<ILogger>();
        }

        private readonly UnicodeBytesConverter _unicoder = new();

        public void SendMessage([NotNull] MessageChannel channel, [NotNull] NetworkToken target, [NotNull] IMessage msg, string msgID)
        {
            if (!CheckDirection())
            {
                throw new MessageDirectionException($"{msg.GetType().Name} cannot be sent to Client.");
            }
            dynamic json = new JObject();
            WriteHeader();
            json.Content = new JObject();
            msg.Serialize(json.Content);
            string jsonTxt = json.ToString(Formatting.None);
            var stringBytes = _unicoder.ConvertToBytes(jsonTxt, startWithLength: false);
            var datapack = new WriteableDatapack();
            datapack.Write(stringBytes.Length)
                .Write(stringBytes);
            datapack.Close();
            SendDatapackTo(datapack, target);

            void WriteHeader()
            {
                json.ChannalName = channel.ChannelName;
                json.MessageID = msgID;
            }

            bool CheckDirection()
            {
                if (channel.Id2MsgTypeAndHandler.TryGetValue(msgID, out var info))
                {
                    var meta = info.meta;
                    if (meta is not null)
                    {
                        return meta.Accept(Direction.ServerToClient);
                    }
                    else
                    {
                        return true;
                    }
                }
                return true;
            }
        }

        public void SendMessageToAll([NotNull] MessageChannel channel, [NotNull] IMessage msg, string msgID)
        {
            foreach (var token in _allConnections.Keys)
            {
                SendMessage(channel, token, msg, msgID);
            }
        }

        public IMessageChannel New(string channelName)
        {
            var channel = new MessageChannel(this, channelName);
            lock (_channelLock)
            {
                _allChannels[channelName] = channel;
            }
            return channel;
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
                    var datapack = Datapack.ReadOne(stream, BufferSize);
                    if (!datapack.IsEmpty)
                    {
                        if (connection.IsConnected)
                        {
                            RecevieDatapack(datapack, token);
                        }
                        else
                        {
                            Logger!.SendWarn($"A datapack from {token.IpAddress} was abandoned because of having been already disconnected.");
                        }
                    }
                }

                RemoveClient(token, () =>
                {
                    if (client.Connected)
                    {
                        client.Client.Shutdown(SocketShutdown.Both);
                    }
                    Logger!.SendWarn($"{token.IpAddress} disconnected.");
                });
            });

            lock (_clientLock)
            {
                _allConnections[token] = (connection, listeningThread);
            }

            listeningThread.Start();
            OnClientConnected?.Invoke(token);
        }

        private void RemoveClient([NotNull] NetworkToken token, Action? afterRemoved = null)
        {
            lock (_clientLock)
            {
                _allConnections.Remove(token);
            }
            afterRemoved?.Invoke();
        }

        public void StopService()
        {
            Logger!.SendMessage("Network component is preparing to stop.");
            _listen?.Interrupt();
            foreach (var (connection, _) in _allConnections.Values)
            {
                var c = connection;
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
            Network.SendMessage(this, target, msg, Msg2Id[msg.GetType()]);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            Network.SendMessageToAll(this, msg, Msg2Id[msg.GetType()]);
        }

        public Dictionary<string, (Type msg, dynamic? handler, MsgAttribute? meta)> Id2MsgTypeAndHandler
        {
            get;
        } = new();
        public Dictionary<Type, string> Msg2Id
        {
            get;
        } = new();
        private readonly object _msgLock = new();

        public void RegisterMessageHandler<Msg, Handler>(string messageID)
            where Msg : class, IMessage, new()
            where Handler : class, IMessageHandler<Msg>, new()
        {
            var msg = typeof(Msg);
            var attrs = msg.GetCustomAttributes<MsgAttribute>().ToArray();
            var meta = attrs.Length > 0 ? attrs[0] : null;
            lock (_msgLock)
            {
                Msg2Id[msg] = messageID;
                Id2MsgTypeAndHandler[messageID] = (msg, new Handler(), meta);
            }
        }

        public void RegisterMessage<Msg>(string messageID) where Msg : class, IMessage, new()
        {
            var msg = typeof(Msg);
            var attrs = msg.GetCustomAttributes<MsgAttribute>().ToArray();
            var meta = attrs.Length > 0 ? attrs[0] : null;
            lock (_msgLock)
            {
                Msg2Id[msg] = messageID;
                Id2MsgTypeAndHandler[messageID] = (msg, null, meta);
            }
        }
        public void RegisterMessageHandler<Msg, Handler>()
            where Msg : class, IMessage, new()
            where Handler : class, IMessageHandler<Msg>, new()
        {
            var msg = typeof(Msg);
            var attrs = msg.GetCustomAttributes<MsgAttribute>().ToArray();
            if (attrs.Length > 0)
            {
                var nameAttr = attrs[0];
                var name = nameAttr.Name;
                if (string.IsNullOrEmpty(name))
                {
                    throw new MessageTypeHasNoNameException(msg.FullName ?? msg.Name);
                }
                lock (_msgLock)
                {
                    Msg2Id[msg] = name;
                    Id2MsgTypeAndHandler[name] = (msg, new Handler(), nameAttr);
                }
            }
            else
            {
                throw new MessageTypeHasNoNameException(msg.FullName ?? msg.Name);
            }
        }

        public void RegisterMessage<Msg>() where Msg : class, IMessage, new()
        {
            var msg = typeof(Msg);
            var attrs = msg.GetCustomAttributes<MsgAttribute>().ToArray();
            if (attrs.Length > 0)
            {
                var nameAttr = attrs[0];
                var name = nameAttr.Name;
                if (string.IsNullOrEmpty(name))
                {
                    throw new MessageTypeHasNoNameException(msg.FullName ?? msg.Name);
                }
                lock (_msgLock)
                {
                    Msg2Id[msg] = name;
                    Id2MsgTypeAndHandler[name] = (msg, null, nameAttr);
                }
            }
            else
            {
                throw new MessageTypeHasNoNameException(msg.FullName ?? msg.Name);
            }
        }

        public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null)
        {
            if (Id2MsgTypeAndHandler.TryGetValue(messageID, out var info))
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
