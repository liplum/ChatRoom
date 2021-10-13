using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Networks;
public interface IMessageChannel
{
    public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg);
    public void SendMessageToAll([NotNull] IMessage msg);
    public void ReceiveMessage(int messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null);

    public void RegisterMessageType<MessageType, HandlerType>(int messageID) where MessageType : class, IMessage, new() where HandlerType : class, IMessageHandler<MessageType>, new();

    public string ChannelName
    {
        get;
    }
}