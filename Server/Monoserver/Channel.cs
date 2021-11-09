using ChattingRoom.Core.Networks;
using System.Net.Sockets;
using System.Reflection;
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

        public Dictionary<string, (Type msg, dynamic? handler, MsgAttribute? meta)> Id2MsgTypeAndHandler
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
                dynamic? msg;
                try
                {
                    msg = Activator.CreateInstance(info.msg);
                }
                catch
                {
                    Network.Logger!.SendError($"Cannot create Message<{info.msg.FullName ?? info.msg.Name}> object");
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

