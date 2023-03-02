using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Network;
using ChatRoom.Core.Ternimal;
using ChatRoom.Core.Util;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WebSocketSharp.Server;
using static ChatRoom.Core.Network.INetwork;

namespace ChatRoom.Server;

public partial class ChatRoomServer : IServer
{
    private class Network : WebSocketBehavior, INetwork
    {
        private static readonly string EmptyJObjectStr = new JObject().ToString();
        private readonly Dictionary<string, IMessageChannel> _allChannels = new();
        private readonly Dictionary<NetworkToken, (IConnection connection, Thread listning)> _allConnections = new();
        private readonly object _channelLock = new();
        private readonly object _clientLock = new();

        private readonly UnicodeBytesConverter _unicoder = new();

        private int _buffSize = 1024;

        public Network(ChatRoomServer server)
        {
            Server = server;
            MsgSendingThread = new(() =>
            {
                foreach (var task in SendTasks.GetConsumingEnumerable())
                    task.Start();
            })
            {
                IsBackground = true
            };
            MsgAnalysisThread = new(() =>
            {
                foreach (var task in AnalyzeMsgTasks.GetConsumingEnumerable())
                    task.Start();
            })
            {
                IsBackground = true
            };
        }

        private Thread MsgSendingThread { get; }
        private Thread MsgAnalysisThread { get; }
#nullable disable
        public ILoggerManager LoggerManager { get; set; }
#nullable enable
        private Thread? Listen { get; set; }
        private BlockingCollection<Task> SendTasks { get; } = new();
        private BlockingCollection<Task> AnalyzeMsgTasks { get; } = new();

        public ChatRoomServer Server { get; }

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
                        if (info.Value.connection.IsConnected)
                            yield return info.Key;
                }
            }
        }

        public void SendDatapackTo(IDatapack datapack, NetworkToken token)
        {
            (IConnection connection, Thread listning) info;
            lock (_clientLock)
            {
                _allConnections.TryGetValue(token, out info);
            }

            if (info != default)
            {
                var connection = info.connection;
                if (connection.IsConnected)
                    try
                    {
                        connection.Send(datapack);
                    }
                    catch (Exception)
                    {
                        LoggerManager!.SendError($"Cannot write datapack to {token.IpAddress}.");
                    }
            }
        }


        public void Initialize(IServiceProvider serviceProvider)
        {
            LoggerManager = serviceProvider.Resolve<ILoggerManager>();
        }

        public void ReceiveDatapack(IDatapack datapack, NetworkToken? token = null)
        {
            AddAnaylzeTask(() =>
            {
                try
                {
                    var jsonString = _unicoder.ConvertToString(datapack.ToBytes());
                    jsonString = jsonString.Trim();
                    dynamic json = JObject.Parse(jsonString);
                    OnMessagePreAnalyze?.Invoke(token, jsonString, json);
                    string? channelName = json.ChannelName;
                    string? messageId = json.MessageID;
                    var content = json.Content ?? new JObject();
                    if (!(channelName, messageId).NotNull())
                    {
                        LoggerManager.SendError($"Cannot analyse datapack: \"{jsonString}\" because of no header.");
                        return;
                    }

                    IMessageChannel? channel;
                    lock (_channelLock)
                    {
                        _allChannels.TryGetValue(channelName, out channel);
                    }

                    if (channel is not null)
                    {
                        if (channel.CanPass(messageId, Direction.ClientToServer))
                            channel.OnReceive(messageId, content, token);
                        else LoggerManager!.SendMessage($"Message<{messageId}> cannot pass the Channel<{channelName}>.");
                    }
                    else
                    {
                        LoggerManager.SendError($"Cannot find channel called {channelName}");
                    }
                }
                catch (Exception e)
                {
                    LoggerManager.SendError($"Cannot analyse datapack from {token?.IpAddress},because {e.Message}");
                }
            });
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

        public  WebSocketServer? ws { get; set; }

        public void StartService()
        {
            LoggerManager.SendMessage("Network component is preparing to start.");
            var port = (int)Assets.Configs.Port;
            ws = new WebSocketServer(port);

            ws.AddWebSocketService("/", () => this);
            ws.Start();
            LoggerManager.SendMessage("Network component started.");
            Listen = new(() =>
            {
                while (true)
                {
                    var client = _serverSocket.AcceptTcpClient();
                    if (client.Client.RemoteEndPoint is IPEndPoint ipEndPoint)
                    {
                        var ip = ipEndPoint.Address;
                        var token = new NetworkToken(ip);
                        LoggerManager.SendWarn($"{ip} connected.");
                        AddNewClient(token, client);
                    }
                }
            });
            Listen.Start();
            MsgSendingThread.Start();
            MsgAnalysisThread.Start();
            LoggerManager.SendMessage("Server started listening connection of clients.");
        }

        public void StopService()
        {
            LoggerManager!.SendMessage("Network component is preparing to stop.");
            ws?.Stop();
            Listen?.Interrupt();
            foreach (var (connection, _) in _allConnections.Values)
            {
                connection.Terminal();
            }

            LoggerManager!.SendMessage("Network component stoped.");
        }

        public bool IsConnected(NetworkToken token)
        {
            return _allConnections.TryGetValue(token, out var info) &&
                   info.connection.IsConnected;
        }

        public IMessageChannel? GetMessageChannelBy(string name)
        {
            return _allChannels.TryGetValue(name, out var channel) ? channel : null;
        }


        public void AddSendTask(Action task)
        {
            SendTasks.Add(new(task));
        }

        public void AddAnaylzeTask(Action task)
        {
            AnalyzeMsgTasks.Add(new(task));
        }

        public void SendMessage(MessageChannel channel, NetworkToken target, IMessage msg, string msgId)
        {
            AddSendTask(() =>
            {
                if (!_allConnections.TryGetValue(target, out var info) || !info.connection.IsConnected)
                {
                    LoggerManager!.SendError(
                        $"Cannot send message<{msgId}> to {target.IpAddress} who has been already disconnected.");
                    return;
                }

                if (!channel.CanPass(msgId, Direction.ServerToClient))
                    throw new MessageDirectionException($"{msg.GetType().Name} cannot be sent to Client.");
                dynamic json = new JObject();
                WriteHeader();
                json.Content = new JObject();
                try
                {
                    msg.Serialize(json.Content);
                }
                catch (Exception e)
                {
                    LoggerManager!.SendError($"Cannot serialize Message<{msgId}>\nBecause {e.Message}\n{e.StackTrace}");
                    return;
                }

                string jsonTxt = json.ToString(Formatting.None);
                var stringBytes = _unicoder.ConvertToBytes(jsonTxt, false);
                var datapack = new WriteableDatapack();
                datapack.Write(stringBytes.Count)
                    .Write(stringBytes);
                datapack.Close();
                SendDatapackTo(datapack, target);

                void WriteHeader()
                {
                    json.ChannelName = channel.ChannelName;
                    json.MessageID = msgId;
                    json.TimeStamp = DateTimeOffset.Now.ToUnixTimeSeconds();
                }
            });
        }

        public void SendMessageToAll(MessageChannel channel, IMessage msg, string msgId)
        {
            foreach (var token in _allConnections.Keys) SendMessage(channel, token, msg, msgId);
        }

        private void AddNewClient(NetworkToken token, TcpClient client)
        {
            var connection = new SocketConnection(this, token, client);
            connection.Connect();
            var listeningThread = new Thread(() =>
            {
                using var stream = client.GetStream();
                while (true)
                {
                    if (!client.Connected) break;
                    var datapack = Datapack.ReadOne(stream, BufferSize);
                    if (!datapack.IsEmpty)
                    {
                        if (connection.IsConnected) ReceiveDatapack(datapack, token);
                        else
                            LoggerManager!.SendWarn(
                                $"A datapack from {token.IpAddress} was abandoned because of having been already disconnected.");
                    }
                }

                client.Close();
                RemoveClient(token, () =>
                {
                    if (client.Connected) client.Client.Shutdown(SocketShutdown.Both);
                    LoggerManager!.SendWarn($"{token.IpAddress} disconnected.");
                });
            });

            lock (_clientLock)
            {
                _allConnections[token] = (connection, listeningThread);
            }

            listeningThread.Start();
            OnClientConnected?.Invoke(token);
        }

        private void RemoveClient(NetworkToken token, Action? afterRemoved = null)
        {
            lock (_clientLock)
            {
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