using System.Runtime.Serialization;

namespace ChatRoom.Core.Network;

public interface IMessageChannel
{
    public delegate void OnMessageHandledHandler(NetworkToken? token, IMessage message, dynamic handler);

    public delegate void OnMessageReceivedHandler(NetworkToken? token, IMessage message, dynamic? handler);

    public string ChannelName { get; }

    /// <summary>
    /// </summary>
    /// <param name="target"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessage(NetworkToken target, IMessage msg);

    /// <summary>
    /// </summary>
    /// <param name="targets"></param>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessage(IEnumerable<NetworkToken> targets, IMessage msg)
    {
        foreach (var target in targets) SendMessage(target, msg);
    }

    /// <summary>
    /// </summary>
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessageToAll(IMessage msg);

    public bool CanPass(string msgId, params Direction[] directions);


    public void OnReceive(string messageId, dynamic jsonContent, NetworkToken? token = null);

    public void Register(Type msgType, Func<IMessage> msgGetter, Func<object>? handlerGetter = null,
        string? msgId = null);

    public event OnMessageHandledHandler OnMessageHandled;

    public event OnMessageReceivedHandler OnMessageReceived;
}

public static class MessageChannelHelper
{
    public static void Register<TMsg, THandler>(this IMessageChannel channel, Func<TMsg> msgGetter,
        Func<THandler> handlerGetter, string? msgId = null)
        where TMsg : class, IMessage where THandler : class, IMessageHandler<TMsg>
    {
        channel.Register(typeof(TMsg), msgGetter, handlerGetter, msgId);
    }

    public static void Register<TMsg>(this IMessageChannel channel, Func<TMsg> msgGetter, string? msgId = null)
        where TMsg : class, IMessage
    {
        channel.Register(typeof(TMsg), msgGetter, null, msgId);
    }

    public static void Register<TMsg, THandler>(this IMessageChannel channel, string? msgId = null)
        where TMsg : class, IMessage, new() where THandler : class, IMessageHandler<TMsg>, new()
    {
        channel.Register(typeof(TMsg), () => new TMsg(), () => new THandler(), msgId);
    }

    public static void Register<TMsg>(this IMessageChannel channel, string? msgId = null)
        where TMsg : class, IMessage, new()
    {
        channel.Register(typeof(TMsg), () => new TMsg(), null, msgId);
    }
}

[Serializable]
public class MessageDirectionException : Exception
{
    public MessageDirectionException()
    {
    }

    public MessageDirectionException(string message) : base(message)
    {
    }

    public MessageDirectionException(string message, Exception inner) : base(message, inner)
    {
    }

    protected MessageDirectionException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class MessageTypeHasNoNameException : Exception
{
    public MessageTypeHasNoNameException()
    {
    }

    public MessageTypeHasNoNameException(string message) : base(message)
    {
    }

    public MessageTypeHasNoNameException(string message, Exception inner) : base(message, inner)
    {
    }

    protected MessageTypeHasNoNameException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class CannotCreateMsgObjException : Exception
{
    public CannotCreateMsgObjException()
    {
    }

    public CannotCreateMsgObjException(string message) : base(message)
    {
    }

    public CannotCreateMsgObjException(string message, Exception inner) : base(message, inner)
    {
    }

    protected CannotCreateMsgObjException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class CannotCreateHandlerObjException : Exception
{
    public CannotCreateHandlerObjException()
    {
    }

    public CannotCreateHandlerObjException(string message) : base(message)
    {
    }

    public CannotCreateHandlerObjException(string message, Exception inner) : base(message, inner)
    {
    }

    protected CannotCreateHandlerObjException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}