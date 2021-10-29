using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Core.Users;
using System.Diagnostics.CodeAnalysis;
using System.Net.Sockets;
using static ChattingRoom.Core.IServer;
using static ChattingRoom.Core.Networks.INetwork;
using IServiceProvider = ChattingRoom.Core.IServiceProvider;
using Room = ChattingRoom.Core.ChattingRoom;


namespace ChattingRoom.Server;
public class MultiServer : IServer
{
    private readonly ChattingRoomList _chatingRoomList = new();
    private readonly ServiceContainer _serviceContainer = new();
    private readonly Network _network;

    public MultiServer()
    {
        _network = new(this);
    }

    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask([NotNull] Task<Action> action)
    {
        throw new NotImplementedException();
    }

    public UserID GenAvailableUserID()
    {
        throw new NotImplementedException();
    }

    public Room GetChattingRoomBy(ChattingRoomID ID)
    {
        throw new NotImplementedException();
    }

    public IMessageChannel? GetMessageChannelBy(string name)
    {
        throw new NotImplementedException();
    }

    public void Initialize()
    {
        _serviceContainer.RegisterInstance<INetwork, Network>(_network);
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
    }

    public void RegisterUser(UserID userID)
    {
        throw new NotImplementedException();
    }

    public void Start()
    {
        throw new NotImplementedException();
    }

    public bool Verify(UserID id, string password)
    {
        throw new NotImplementedException();
    }

    private class Network : INetwork
    {
        private MultiServer Outer
        {
            get; init;
        }
        public Network(MultiServer outer)
        {
            Outer = outer;
        }

        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, IConnection> _allConnections = new();
        private MultiServer? _bang;

        public event OnClientConnectedHandler? OnClientConnected;

        private Socket? ServerSocket
        {
            get; set;
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            _bang = serviceProvider.Reslove<MultiServer>();
        }

        public IMessageChannel? this[string channelName]
        {
            get => _allChannels.TryGetValue(channelName, out var channel) ? channel : null;
        }

        public IMessageChannel New(string channelName)
        {
            var channel = new MessageChannel(this, channelName);
            _allChannels[channelName] = channel;
            return channel;
        }

        private void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
        }

        private void SendMessageToAll([NotNull] IMessage msg)
        {
        }

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {
            throw new NotImplementedException();
        }

        public void RecevieDatapack([NotNull] IDatapack datapack)
        {
            throw new NotImplementedException();
        }

        public void StartService()
        {
            throw new NotImplementedException();
        }

        public void StopService()
        {
            throw new NotImplementedException();
        }

        public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null)
        {
            throw new NotImplementedException();
        }

        private class MessageChannel : IMessageChannel
        {
            public Network Outter
            {
                get; init;
            }
            public MessageChannel([NotNull] Network outter, [NotNull] string channelName)
            {
                Outter = outter;
                ChannelName = channelName;
            }

            public string ChannelName
            {
                get; init;
            }

            public event IMessageChannel.OnMessageHandledHandler OnMessageHandled;
            public event IMessageChannel.OnMessageReceivedHandler OnMessageReceived;

            public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
            {
                Outter.SendMessage(target, msg);
            }

            public void SendMessageToAll([NotNull] IMessage msg)
            {
                Outter.SendMessageToAll(msg);
            }

            public bool RegisterUser(int UserID)
            {
                throw new NotImplementedException();
            }

            public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null)
            {
                throw new NotImplementedException();
            }

            public void RegisterMessageHandler<Msg, Handler>(string messageID) where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new()
            {
                throw new NotImplementedException();
            }

            public void RegisterMessage<Msg>(string messageID) where Msg : class, IMessage, new()
            {
                throw new NotImplementedException();
            }

            void IMessageChannel.RegisterMessageHandler<Msg, Handler>()
            {
                throw new NotImplementedException();
            }

            void IMessageChannel.RegisterMessage<Msg>()
            {
                throw new NotImplementedException();
            }
        }

        public class SocketConnection : IConnection
        {
            public bool IsConnected => throw new NotImplementedException();

            public bool Connect()
            {
                throw new NotImplementedException();
            }

            public bool Disconnect()
            {
                throw new NotImplementedException();
            }

            public void Send([NotNull] IDatapack datapack)
            {
                throw new NotImplementedException();
            }

            public bool Terminal()
            {
                throw new NotImplementedException();
            }
        }

    }
}
