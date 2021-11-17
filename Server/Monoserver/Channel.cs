using System.Net.Sockets;
using System.Reflection;
using ChattingRoom.Core.Networks;
using static ChattingRoom.Core.Networks.IMessageChannel;

namespace ChattingRoom.Server;

public partial class Monoserver
{
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

        public bool CanPass(string msgID, params Direction[] directions)
        {
            if (Id2MsgTypeAndHandler.TryGetValue(msgID, out var info))
            {
                var meta = info.meta;
                if (meta is not null)
                {
                    var accepted = true;
                    foreach (var dire in directions)
                    {
                        accepted &= meta.Accept(dire);
                    }
                    return accepted;
                }
                else
                {
                    return true;
                }
            }
            return true;
        }

        public Dictionary<string, (Type msgType, Func<IMessage> msgGetter, dynamic? handler, MsgAttribute? meta)> Id2MsgTypeAndHandler
        {
            get;
        } = new();
        public Dictionary<Type, string> Msg2Id
        {
            get;
        } = new();
        private readonly object _msgLock = new();

        public event OnMessageHandledHandler? OnMessageHandled;
        public event OnMessageReceivedHandler? OnMessageReceived;

        public static MsgAttribute? GetMsgAttribute(Type msgType)
        {
            var attrs = msgType.GetCustomAttributes<MsgAttribute>().ToArray();
            return attrs.Length > 0 ? attrs[0] : null;
        }

        public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null)
        {
            if (Id2MsgTypeAndHandler.TryGetValue(messageID, out var info))
            {
                dynamic? msg;
                try
                {
                    msg = info.msgGetter();
                }
                catch
                {
                    Network.Logger!.SendError($"Cannot create Message<{messageID}> object");
                    return;
                }
                if (msg is not null)
                {
                    try
                    {
                        msg.Deserialize(jsonContent);
                    }
                    catch (Exception e)
                    {
                        Network.Logger!.SendError($"Cannot deserialize Message<{messageID}> from \"{jsonContent}\"\nBecause {e.Message}\n{e.StackTrace}");
                        return;
                    }
                    var hanlder = info.handler;
                    OnMessageReceived?.Invoke(token, msg, hanlder);
                    if (hanlder is not null)
                    {
                        var context = new MessageContext(Network.Server, this)
                        {
                            ClientToken = token
                        };
                        hanlder.Handle(msg, context);
                        try
                        {
                            OnMessageHandled?.Invoke(token, msg, hanlder);
                        }
                        catch (Exception e)
                        {
                            Network.Logger!.SendError($"Cannot handle Message<{messageID}> from \"{jsonContent}\"\nBecause {e.Message}\n{e.StackTrace}");
                            return;
                        }
                    }
                }
            }
            else
            {
                Network.Logger!.SendError($"Cannot find message type called {messageID}");
            }
        }

        public void RegisterMessage(Type msgType, Func<IMessage> msgGetter, Func<object>? handlerGetter = null, string? msgID = null)
        {
            var handler = handlerGetter?.Invoke();
            var meta = GetMsgAttribute(msgType);
            msgID = msgID is null ? meta?.ID : msgID;
            if (msgID is null)
            {
                throw new MessageTypeHasNoNameException(msgType.FullName ?? msgType.Name);
            }
            lock (_msgLock)
            {
                Msg2Id[msgType] = msgID;
                Id2MsgTypeAndHandler[msgID] = (msgType, msgGetter, handler, meta);
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

        private bool Terminaled
        {
            get; set;
        }

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

