using System.Runtime.Serialization;

namespace ChattingRoom.Core.Networks;
public interface IMessageChannel
{
    /// <summary>
    /// 
    /// </summary>
    /// <param name="target"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg);

    /// <summary>
    /// 
    /// </summary>
    /// <param name="targets"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public virtual void SendMessage([NotNull] IEnumerable<NetworkToken> targets, [NotNull] IMessage msg)
    {
        foreach (var target in targets)
        {
            SendMessage(target, msg);
        }
    }

    /// <summary>
    /// 
    /// </summary>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessageToAll([NotNull] IMessage msg);

    public bool CanPass(string msgID, params Direction[] directions);


    public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null);

    public void RegisterMessage(Type msgType, Func<IMessage> msgGetter, Func<object>? handlerGetter = null, string? msgID = null);

    public virtual void RegisterMessage<Msg, Handler>(Func<Msg> msgGetter, Func<Handler> handlerGetter, string? msgID = null) where Msg : class, IMessage where Handler : class, IMessageHandler<Msg>
    {
        RegisterMessage(typeof(Msg), msgGetter, handlerGetter, msgID);
    }
    public virtual void RegisterMessage<Msg>(Func<Msg> msgGetter, string? msgID = null) where Msg : class, IMessage
    {
        RegisterMessage(typeof(Msg), msgGetter, null, msgID);
    }
    public virtual void RegisterMessage<Msg, Handler>(string? msgID = null) where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new()
    {
        RegisterMessage(typeof(Msg), () => new Msg(), () => new Handler(), msgID);
    }
    public virtual void RegisterMessage<Msg>(string? msgID = null) where Msg : class, IMessage, new()
    {
        RegisterMessage(typeof(Msg), () => new Msg(), null, msgID);
    }

    public string ChannelName
    {
        get;
    }


    public event OnMessageHandledHandler OnMessageHandled;

    public event OnMessageReceivedHandler OnMessageReceived;

    public delegate void OnMessageReceivedHandler([AllowNull] NetworkToken token, [NotNull] IMessage message, [AllowNull] dynamic? hanlder);

    public delegate void OnMessageHandledHandler([AllowNull] NetworkToken token, [NotNull] IMessage message, [NotNull] dynamic hanlder);
}



[Serializable]
public class MessageDirectionException : Exception
{
    public MessageDirectionException()
    {
    }
    public MessageDirectionException(string message) : base(message) { }
    public MessageDirectionException(string message, Exception inner) : base(message, inner) { }
    protected MessageDirectionException(
      SerializationInfo info,
      StreamingContext context) : base(info, context) { }
}


[Serializable]
public class MessageTypeHasNoNameException : Exception
{
    public MessageTypeHasNoNameException()
    {
    }
    public MessageTypeHasNoNameException(string message) : base(message) { }
    public MessageTypeHasNoNameException(string message, Exception inner) : base(message, inner) { }
    protected MessageTypeHasNoNameException(
      SerializationInfo info,
      StreamingContext context) : base(info, context) { }
}


[Serializable]
public class CannotCreateMsgObjException : Exception
{
    public CannotCreateMsgObjException()
    {
    }
    public CannotCreateMsgObjException(string message) : base(message) { }
    public CannotCreateMsgObjException(string message, Exception inner) : base(message, inner) { }
    protected CannotCreateMsgObjException(
      SerializationInfo info,
      StreamingContext context) : base(info, context) { }
}


[Serializable]
public class CannotCreateHandlerObjException : Exception
{
    public CannotCreateHandlerObjException()
    {

    }
    public CannotCreateHandlerObjException(string message) : base(message) { }
    public CannotCreateHandlerObjException(string message, Exception inner) : base(message, inner) { }
    protected CannotCreateHandlerObjException(
      SerializationInfo info,
      StreamingContext context) : base(info, context) { }
}