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
    public void SendMessage([NotNull] IEnumerable<NetworkToken> targets, [NotNull] IMessage msg)
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

    public void RegisterMessageHandler<Msg, Handler>(string messageID) where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new();

    public void RegisterMessage<Msg>(string messageID) where Msg : class, IMessage, new();

    /// <summary>
    /// 
    /// </summary>
    /// <typeparam name="Msg"></typeparam>
    /// <typeparam name="Handler"></typeparam>
    /// <exception cref="MessageTypeHasNoNameException"></exception>
    public void RegisterMessageHandler<Msg, Handler>() where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new();

    /// <summary>
    /// 
    /// </summary>
    /// <typeparam name="Msg"></typeparam>
    /// <typeparam name="Handler"></typeparam>
    /// <exception cref="MessageTypeHasNoNameException"></exception>
    public void RegisterMessage<Msg>() where Msg : class, IMessage, new();

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
    public MessageDirectionException() { }
    public MessageDirectionException(string message) : base(message) { }
    public MessageDirectionException(string message, Exception inner) : base(message, inner) { }
    protected MessageDirectionException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}


[Serializable]
public class MessageTypeHasNoNameException : Exception
{
    public MessageTypeHasNoNameException() { }
    public MessageTypeHasNoNameException(string message) : base(message) { }
    public MessageTypeHasNoNameException(string message, Exception inner) : base(message, inner) { }
    protected MessageTypeHasNoNameException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}