using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Server.Protocols;
using System.Diagnostics.CodeAnalysis;
using System.Net;
using System.Net.Sockets;
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
        private readonly Dictionary<NetworkToken, (IConnection, Thread)> _allConnections = new();
        private TcpListener? _serverSocket;
        private readonly object _lock = new();
        private ILogger? Logger
        {
            get; set;
        }

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
            var json = Utils.ConvertToStringWithLengthBeginning(datapack.Bytes);
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            Logger = serviceProvider.Reslove<ILogger>();
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
            return null;
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
                _allConnections[token] = (new SocketConnection(this, token), listeningThread);
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
        private Network Outer
        {
            get; init;
        }

        private NetworkToken Token
        {
            get; init;
        }

        public SocketConnection(Network outer, NetworkToken token)
        {
            Outer = outer;
            Token = token;
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
