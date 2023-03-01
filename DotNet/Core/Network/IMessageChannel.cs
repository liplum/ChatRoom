using System.Diagnostics.CodeAnalysis;
using System.Runtime.Serialization;

namespace ChatRoom.Core.Network;
public interface IMessageChannel {

    public delegate void OnMessageHandledHandler([AllowNull] NetworkToken token, [NotNull] IMessage message, [NotNull] dynamic hanlder);

    public delegate void OnMessageReceivedHandler([AllowNull] NetworkToken token, [NotNull] IMessage message, [AllowNull] dynamic? hanlder);

    public string ChannelName {
        get;
    }
    /// <summary>
    /// </summary>
    /// <param name="target"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg);

    /// <summary>
    /// </summary>
    /// <param name="targets"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public virtual void SendMessage([NotNull] IEnumerable<NetworkToken> targets, [NotNull] IMessage msg) {
        foreach (var target in targets) SendMessage(target, msg);
    }

    /// <summary>
    /// </summary>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessageToAll([NotNull] IMessage msg);

    public bool CanPass(string msgId, params Direction[] directions);


    public void ReceiveMessage(string messageId, dynamic jsonContent, [AllowNull] NetworkToken token = null);

    public void RegisterMessage(Type msgType, Func<IMessage> msgGetter, Func<object>? handlerGetter = null, string? msgId = null);

    public virtual void RegisterMessage<TMsg, THandler>(Func<TMsg> msgGetter, Func<THandler> handlerGetter, string? msgId = null)
        where TMsg : class, IMessage where THandler : class, IMessageHandler<TMsg> {
        RegisterMessage(typeof(TMsg), msgGetter, handlerGetter, msgId);
    }
    public virtual void RegisterMessage<TMsg>(Func<TMsg> msgGetter, string? msgId = null) where TMsg : class, IMessage {
        RegisterMessage(typeof(TMsg), msgGetter, null, msgId);
    }
    public virtual void RegisterMessage<TMsg, THandler>(string? msgId = null) where TMsg : class, IMessage, new() where THandler : class, IMessageHandler<TMsg>, new() {
        RegisterMessage(typeof(TMsg), () => new TMsg(), () => new THandler(), msgId);
    }
    public virtual void RegisterMessage<TMsg>(string? msgId = null) where TMsg : class, IMessage, new() {
        RegisterMessage(typeof(TMsg), () => new TMsg(), null, msgId);
    }


    public event OnMessageHandledHandler OnMessageHandled;

    public event OnMessageReceivedHandler OnMessageReceived;
}

[Serializable]
public class MessageDirectionException : Exception {
    public MessageDirectionException() {
    }
    public MessageDirectionException(string message) : base(message) { }
    public MessageDirectionException(string message, Exception inner) : base(message, inner) { }
    protected MessageDirectionException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}

[Serializable]
public class MessageTypeHasNoNameException : Exception {
    public MessageTypeHasNoNameException() {
    }
    public MessageTypeHasNoNameException(string message) : base(message) { }
    public MessageTypeHasNoNameException(string message, Exception inner) : base(message, inner) { }
    protected MessageTypeHasNoNameException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}

[Serializable]
public class CannotCreateMsgObjException : Exception {
    public CannotCreateMsgObjException() {
    }
    public CannotCreateMsgObjException(string message) : base(message) { }
    public CannotCreateMsgObjException(string message, Exception inner) : base(message, inner) { }
    protected CannotCreateMsgObjException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}

[Serializable]
public class CannotCreateHandlerObjException : Exception {
    public CannotCreateHandlerObjException() {

    }
    public CannotCreateHandlerObjException(string message) : base(message) { }
    public CannotCreateHandlerObjException(string message, Exception inner) : base(message, inner) { }
    protected CannotCreateHandlerObjException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}