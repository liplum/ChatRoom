using ChattingRoom.Core.Networks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Net;
using System.Net.Sockets;
using static ChattingRoom.Core.Networks.INetwork;

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
        internal ILogger? Logger
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

        public IEnumerable<NetworkToken> AllConnectedClient
        {
            get
            {
                lock (_clientLock)
                {
                    foreach (var info in _allConnections)
                    {
                        if (info.Value.connection.IsConnected)
                        {
                            yield return info.Key;
                        }
                    }
                }
            }
        }

        #region Event
        public event OnClientConnectedHandler? OnClientConnected;
        public event OnMessagePreAnalyzeHandler? OnMessagePreAnalyze;
        #endregion

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token)
        {
            lock (_clientLock)
            {
                if (_allConnections.TryGetValue(token, out var info))
                {
                    var connection = info.connection;
                    try
                    {
                        connection.Send(datapack);
                    }
                    catch (Exception)
                    {
                        Logger!.SendError($"Cannot write datapack to {token.IpAddress}.");
                    }
                }
            }
        }
        private static readonly string EmptyJObjectStr = new JObject().ToString();
        public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null)
        {
            try
            {
                var jsonString = _unicoder.ConvertToString(datapack.ToBytes());
                jsonString = jsonString.Trim();
                dynamic json = JObject.Parse(jsonString);
                OnMessagePreAnalyze?.Invoke(token, jsonString, json);
                string? channelName = json.ChannelName;
                string? messageID = json.MessageID;
                dynamic content = json.Content ?? new JObject();

                lock (_channelLock)
                {
                    if ((channelName, messageID).NotNull())
                    {
                        if (_allChannels.TryGetValue(channelName, out var channel))
                        {
                            if (channel.CanPass(messageID, Direction.ClientToServer))
                            {
                                channel.ReceiveMessage(messageID, content, token);
                            }
                            else
                            {
                                Logger!.SendMessage($"Message<{messageID}> cannot pass the Channel<{channelName}>.");
                            }
                        }
                        else
                        {
                            Logger!.SendError($"Cannot find channel called {channelName}");
                        }
                    }
                    else
                    {
                        Logger!.SendError($"Cannot analyse datapack: \"{jsonString}\" because of no header.");
                    }
                }
            }
            catch (Exception e)
            {
                Logger!.SendError($"Cannot analyse datapack from {token?.IpAddress},because {e.Message}");
            }
        }

        public void Initialize(IServiceProvider serviceProvider)
        {
            Logger = serviceProvider.Reslove<ILogger>();
        }

        private readonly UnicodeBytesConverter _unicoder = new();

        public void SendMessage([NotNull] MessageChannel channel, [NotNull] NetworkToken target, [NotNull] IMessage msg, string msgID)
        {
            if (!_allConnections.TryGetValue(target, out var info) || !info.connection.IsConnected)
            {
                Logger!.SendError($"Cannot send message<{msgID}> to {target.IpAddress} who has been already disconnected.");
                return;
            }

            if (!channel.CanPass(msgID, Direction.ServerToClient))
            {
                throw new MessageDirectionException($"{msg.GetType().Name} cannot be sent to Client.");
            }
            dynamic json = new JObject();
            WriteHeader();
            json.Content = new JObject();
            try
            {
                msg.Serialize(json.Content);
            }
            catch (Exception e)
            {
                Logger!.SendError($"Cannot serialize Message<{msgID}>\nBecause {e.Message}\n{e.StackTrace}");
                return;
            }
            string jsonTxt = json.ToString(Formatting.None);
            var stringBytes = _unicoder.ConvertToBytes(jsonTxt, startWithLength: false);
            var datapack = new WriteableDatapack();
            datapack.Write(stringBytes.Count)
                .Write(stringBytes);
            datapack.Close();
            SendDatapackTo(datapack, target);

            void WriteHeader()
            {
                json.ChannelName = channel.ChannelName;
                json.MessageID = msgID;
                json.TimeStamp = DateTimeOffset.Now.ToUnixTimeSeconds();
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
            int port = (int)Assets.Configs.Port;
            _serverSocket = new TcpListener(IPAddress.Any, port);
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

        public bool IsConnected([NotNull] NetworkToken token)
        {
            if (_allConnections.TryGetValue(token, out var info))
            {
                return info.connection.IsConnected;
            }
            return false;
        }

        public IMessageChannel? GetMessageChannelBy(string name)
        {
            if (_allChannels.TryGetValue(name, out var channel))
            {
                return channel;
            }
            return null;
        }
    }
}
