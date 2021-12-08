using System.Net.Sockets;
using System.Reflection;
using ChattingRoom.Core.Networks;
using static ChattingRoom.Core.Networks.IMessageChannel;

namespace ChattingRoom.Server;
public partial class Monoserver {
    private class MessageChannel : IMessageChannel {
        private readonly object _msgLock = new();

        public MessageChannel([NotNull] Network network, [NotNull] string channelName) {
            Network = network;
            ChannelName = channelName;
        }
        public Network Network {
            get;
        }

        private Dictionary<string, (Type msgType, Func<IMessage> msgGetter, dynamic? handler, MsgAttribute? meta)>
            Id2MsgTypeAndHandler { get; } = new();

        private Dictionary<Type, string> Msg2Id { get; } = new();

        public string ChannelName {
            get;
        }

        public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg) {
            Network.SendMessage(this, target, msg, Msg2Id[msg.GetType()]);
        }

        public void SendMessageToAll([NotNull] IMessage msg) {
            Network.SendMessageToAll(this, msg, Msg2Id[msg.GetType()]);
        }

        public bool CanPass(string msgId, params Direction[] directions) {
            if (!Id2MsgTypeAndHandler.TryGetValue(msgId, out var info)) return true;
            var meta = info.meta;
            return meta is null || directions.Aggregate(true, (current, dire) => current & meta.Accept(dire));
        }

        public event OnMessageHandledHandler? OnMessageHandled;
        public event OnMessageReceivedHandler? OnMessageReceived;

        public void ReceiveMessage(string messageId, dynamic jsonContent, NetworkToken? token = null) {
            if (Id2MsgTypeAndHandler.TryGetValue(messageId, out var info)) {
                IMessage msg;
                try {
                    msg = info.msgGetter();
                }
                catch {
                    Network.Logger!.SendError($"Cannot create Message<{messageId}> object");
                    return;
                }
                try {
                    msg.Deserialize(jsonContent);
                }
                catch (Exception e) {
                    Network.Logger!.SendError(
                        $"Cannot deserialize Message<{messageId}> from \"{jsonContent}\"\nBecause {e.Message}\n{e.StackTrace}");
                    return;
                }

                var handler = info.handler;
                OnMessageReceived?.Invoke(token, msg, handler);
                if (handler is null) return;
                var context = new MessageContext(Network, Network.Server, this) {
                    ClientToken = token
                };
                handler.Handle(msg, context);
                try {
                    OnMessageHandled?.Invoke(token, msg, handler);
                }
                catch (Exception e) {
                    Network.Logger!.SendError(
                        $"Cannot handle Message<{messageId}> from \"{jsonContent}\"\nBecause {e.Message}\n{e.StackTrace}");
                }
            }
            else {
                Network.Logger!.SendError($"Cannot find message type called {messageId}");
            }
        }

        public void RegisterMessage(Type msgType, Func<IMessage> msgGetter, Func<object>? handlerGetter = null,
            string? msgId = null) {
            var handler = handlerGetter?.Invoke();
            var meta = GetMsgAttribute(msgType);
            msgId = msgId is null ? meta?.Id : msgId;
            if (msgId is null) throw new MessageTypeHasNoNameException(msgType.FullName ?? msgType.Name);

            lock (_msgLock) {
                Msg2Id[msgType] = msgId;
                Id2MsgTypeAndHandler[msgId] = (msgType, msgGetter, handler, meta);
            }
        }

        private static MsgAttribute? GetMsgAttribute(Type msgType) {
            var attrs = msgType.GetCustomAttributes<MsgAttribute>().ToArray();
            return attrs.Length > 0 ? attrs[0] : null;
        }
    }

    private class SocketConnection : IConnection {

        public SocketConnection(Network outer, NetworkToken token, TcpClient tcpClient) {
            Outer = outer;
            Token = token;
            TcpClient = tcpClient;
            Socket = tcpClient.Client;
            Stream = tcpClient.GetStream();
        }
        public NetworkStream Stream {
            get;
        }
        public TcpClient TcpClient {
            get;
        }

        public Socket Socket {
            get;
        }

        public Network Outer {
            get;
        }

        private bool Terminaled { get; set; }

        private NetworkToken Token {
            get;
        }

        public bool Terminal() {
            if (Terminaled) return false;

            Disconnect();
            Terminaled = true;
            Socket.Close();
            return true;
        }

        public bool IsConnected { get; private set; }

        public bool Connect() {
            if (IsConnected) return false;

            IsConnected = true;
            return true;
        }

        public bool Disconnect() {
            if (!IsConnected) return false;

            IsConnected = false;
            return true;
        }

        public void Send([NotNull] IDatapack datapack) {
            if (!IsConnected) throw new ConnectionClosedException();

            if (Stream.CanWrite) datapack.WriteInto(Stream);
        }
    }
}