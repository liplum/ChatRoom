using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Networks;
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
    /// <param name="msg"></param>
    /// <exception cref="MessageDirectionException"></exception>
    public void SendMessageToAll([NotNull] IMessage msg);

    public void ReceiveMessage(string messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null);

    public void RegisterMessageHandler<Msg, Handler>(string messageID) where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new();

    public void RegisterMessage<Msg>(string messageID) where Msg : class, IMessage, new();

    public string ChannelName
    {
        get;
    }
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