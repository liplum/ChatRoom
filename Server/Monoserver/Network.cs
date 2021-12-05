using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using ChattingRoom.Core.Networks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using static ChattingRoom.Core.Networks.INetwork;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer {
    private class Network : INetwork {
        private static readonly string EmptyJObjectStr = new JObject().ToString();
        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, (IConnection connection, Thread listning)> _allConnections = new();
        private readonly object _channelLock = new();
        private readonly object _clientLock = new();

        private readonly UnicodeBytesConverter _unicoder = new();

        private int _buffSize = 1024;
        private TcpListener? _serverSocket;

        public Network(Monoserver server) {
            Server = server;
            MsgSendingThread = new(() => {
                foreach (var task in SendTasks.GetConsumingEnumerable()) task?.Start();
            }) {
                IsBackground = true
            };
            MsgAnalysisThread = new(() => {
                foreach (var task in AnalyzeMsgTasks.GetConsumingEnumerable()) task?.Start();
            }) {
                IsBackground = true
            };
        }
        private Thread MsgSendingThread {
            get;
        }
        private Thread MsgAnalysisThread {
            get;
        }
#nullable disable
        public ILogger Logger {
            get;
            set;
        }
#nullable enable
        private Thread? Listen {
            get;
            set;
        }
        private BlockingCollection<Task> SendTasks {
            get;
        } = new();
        private BlockingCollection<Task> AnalyzeMsgTasks {
            get;
        } = new();

        public Monoserver Server {
            get;
        }
        public int BufferSize {
            get => _buffSize;
            set {
                if (value <= 0)
                    throw new ArgumentOutOfRangeException(nameof(BufferSize));
                _buffSize = value;
            }
        }

        public IEnumerable<NetworkToken> AllConnectedClient {
            get {
                lock (_clientLock) {
                    foreach (var info in _allConnections)
                        if (info.Value.connection.IsConnected)
                            yield return info.Key;
                }
            }
        }

        public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token) {
            (IConnection connection, Thread listning) info;
            lock (_clientLock) {
                _allConnections.TryGetValue(token, out info);
            }
            if (info != default) {
                var connection = info.connection;
                if (connection.IsConnected)
                    try {
                        connection.Send(datapack);
                    }
                    catch (Exception) {
                        Logger!.SendError($"Cannot write datapack to {token.IpAddress}.");
                    }
            }
        }


        public void Initialize(IServiceProvider serviceProvider) {
            Logger = serviceProvider.Resolve<ILogger>();
        }

        public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null) {
            AddAnaylzeTask(() => {
                try {
                    var jsonString = _unicoder.ConvertToString(datapack.ToBytes());
                    jsonString = jsonString.Trim();
                    dynamic json = JObject.Parse(jsonString);
                    OnMessagePreAnalyze?.Invoke(token, jsonString, json);
                    string? channelName = json.ChannelName;
                    string? messageId = json.MessageID;
                    var content = json.Content ?? new JObject();
                    if (!(channelName, messageId).NotNull()) {
                        Logger.SendError($"Cannot analyse datapack: \"{jsonString}\" because of no header.");
                        return;
                    }

                    IMessageChannel? channel;
                    lock (_channelLock) {
                        _allChannels.TryGetValue(channelName, out channel);
                    }
                    if (channel is not null) {
                        if (channel.CanPass(messageId, Direction.ClientToServer)) channel.ReceiveMessage(messageId, content, token);
                        else Logger!.SendMessage($"Message<{messageId}> cannot pass the Channel<{channelName}>.");
                    }
                    else {
                        Logger.SendError($"Cannot find channel called {channelName}");
                    }
                }
                catch (Exception e) {
                    Logger.SendError($"Cannot analyse datapack from {token?.IpAddress},because {e.Message}");
                }
            });
        }

        public IMessageChannel New(string channelName) {
            var channel = new MessageChannel(this, channelName);
            lock (_channelLock) {
                _allChannels[channelName] = channel;
            }
            return channel;
        }


        public void StartService() {
            Logger.SendMessage("Network component is preparing to start.");
            var port = (int)Assets.Configs.Port;
            _serverSocket = new(IPAddress.Any, port);
            _serverSocket.Start();
            Logger.SendMessage("Network component started.");
            Listen = new(() => {
                while (true) {
                    var client = _serverSocket.AcceptTcpClient();
                    if (client.Client.RemoteEndPoint is IPEndPoint ipEndPoint) {
                        var ip = ipEndPoint.Address;
                        var token = new NetworkToken(ip);
                        Logger.SendWarn($"{ip} connected.");
                        AddNewClient(token, client);
                    }
                }
            });
            Listen.Start();
            MsgSendingThread.Start();
            MsgAnalysisThread.Start();
            Logger.SendMessage("Server started listening connection of clients.");
        }

        public void StopService() {
            Logger!.SendMessage("Network component is preparing to stop.");
            _serverSocket?.Stop();
            Listen?.Interrupt();
            foreach (var (connection, _) in _allConnections.Values) {
                var c = connection;
                c.Terminal();
            }
            Logger!.SendMessage("Network component stoped.");
        }

        public bool IsConnected([NotNull] NetworkToken token) {
            if (_allConnections.TryGetValue(token, out var info)) return info.connection.IsConnected;
            return false;
        }

        public IMessageChannel? GetMessageChannelBy(string name) {
            if (_allChannels.TryGetValue(name, out var channel)) return channel;
            return null;
        }


        public void AddSendTask([NotNull] Action task) {
            SendTasks.Add(new(task));
        }
        public void AddAnaylzeTask([NotNull] Action task) {
            AnalyzeMsgTasks.Add(new(task));
        }

        public void SendMessage([NotNull] MessageChannel channel, [NotNull] NetworkToken target, [NotNull] IMessage msg, string msgId) {
            AddSendTask(() => {
                if (!_allConnections.TryGetValue(target, out var info) || !info.connection.IsConnected) {
                    Logger!.SendError($"Cannot send message<{msgId}> to {target.IpAddress} who has been already disconnected.");
                    return;
                }

                if (!channel.CanPass(msgId, Direction.ServerToClient)) throw new MessageDirectionException($"{msg.GetType().Name} cannot be sent to Client.");
                dynamic json = new JObject();
                WriteHeader();
                json.Content = new JObject();
                try {
                    msg.Serialize(json.Content);
                }
                catch (Exception e) {
                    Logger!.SendError($"Cannot serialize Message<{msgId}>\nBecause {e.Message}\n{e.StackTrace}");
                    return;
                }
                string jsonTxt = json.ToString(Formatting.None);
                var stringBytes = _unicoder.ConvertToBytes(jsonTxt, false);
                var datapack = new WriteableDatapack();
                datapack.Write(stringBytes.Count)
                    .Write(stringBytes);
                datapack.Close();
                SendDatapackTo(datapack, target);

                void WriteHeader() {
                    json.ChannelName = channel.ChannelName;
                    json.MessageID = msgId;
                    json.TimeStamp = DateTimeOffset.Now.ToUnixTimeSeconds();
                }
            });
        }

        public void SendMessageToAll([NotNull] MessageChannel channel, [NotNull] IMessage msg, string msgId) {
            foreach (var token in _allConnections.Keys) SendMessage(channel, token, msg, msgId);
        }

        private void AddNewClient([NotNull] NetworkToken token, [NotNull] TcpClient client) {
            var connection = new SocketConnection(this, token, client);
            connection.Connect();
            var listeningThread = new Thread(() => {
                using var stream = client.GetStream();
                while (true) {
                    if (!client.Connected) break;
                    var datapack = Datapack.ReadOne(stream, BufferSize);
                    if (!datapack.IsEmpty) {
                        if (connection.IsConnected) RecevieDatapack(datapack, token);
                        else Logger!.SendWarn($"A datapack from {token.IpAddress} was abandoned because of having been already disconnected.");
                    }
                }
                client.Close();
                RemoveClient(token, () => {
                    if (client.Connected) client.Client.Shutdown(SocketShutdown.Both);
                    Logger!.SendWarn($"{token.IpAddress} disconnected.");
                });
            });

            lock (_clientLock) {
                _allConnections[token] = (connection, listeningThread);
            }

            listeningThread.Start();
            OnClientConnected?.Invoke(token);
        }

        private void RemoveClient([NotNull] NetworkToken token, Action? afterRemoved = null) {
            lock (_clientLock) {
                _allConnections.Remove(token);
            }
            afterRemoved?.Invoke();
            OnClientDisconnected?.Invoke(token);
        }

        #region Event
        public event OnClientConnectedHandler? OnClientConnected;
        public event OnMessagePreAnalyzeHandler? OnMessagePreAnalyze;
        public event OnClientDisconnectedHandler? OnClientDisconnected;
        #endregion

    }
}