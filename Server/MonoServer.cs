using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Server.Services;
using System.Diagnostics.CodeAnalysis;
using IServiceProvider = ChattingRoom.Core.IServiceProvider;

namespace ChattingRoom.Server;
public class MonoServer : IServer
{
    private readonly ChatingRoom _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();

    public void Initialize()
    {
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
    }
    private class Network : INetwork
    {
        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, IConnection> _allConnections = new();

        private MonoServer Outer
        {
            get; init;
        }
        public Network(MonoServer outer)
        {
            Outer = outer;
        }

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {

        }

        public void RecevieDatapack([NotNull] IDatapack datapack)
        {
        }

        public void Initialize(IServiceProvider serviceProvider)
        {

        }
        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
            var buf = new ByteBuffer();
            msg.Serialize(buf);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            var buf = new ByteBuffer();
            msg.Serialize(buf);
        }

        public IMessageChannel New(string channelName, ChannelDirection direction)
        {
            throw new NotImplementedException();
        }

        private Thread? _listen;

        public void StartService()
        {
            _listen = new Thread(() =>
            {

            });
        }

        public void StopService()
        {

        }
    }

    private class MessageChannel : IMessageChannel
    {
        public Network Outter
        {
            get; init;
        }
        public MessageChannel([NotNull] Network outter, [NotNull] string channelName, [NotNull] ChannelDirection channelDirection)
        {
            Outter = outter;
            ChannelName = channelName;
            ChannelDirection = channelDirection;
        }

        public string ChannelName
        {
            get; init;
        }

        public ChannelDirection ChannelDirection
        {
            get; init;
        }

        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg)
        {
            Outter.SendMessage(target, msg);
        }

        public void SendMessageToAll([NotNull] IMessage msg)
        {
            Outter.SendMessageToAll(msg);
        }
    }
    private class SocketConnection : IConnection
    {

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
            return true;
        }

        public bool Disconnect()
        {
            if (!IsConnected)
            {
                return false;
            }

            return true;
        }

        public void Send(IDatapack datapack)
        {

        }
    }
}
