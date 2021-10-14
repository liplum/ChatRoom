using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Networks;
public interface IMessageChannel
{
    public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg);
    public void SendMessageToAll([NotNull] IMessage msg);
    public void ReceiveMessage(int messageID, dynamic jsonContent, [AllowNull] NetworkToken token = null);

    public void RegisterMessageHandler<Msg, Handler>(string messageID) where Msg : class, IMessage, new() where Handler : class, IMessageHandler<Msg>, new();

    public void RegisterMessage<Msg>(string messageID) where Msg:class,IMessage,new();
    public bool RegisterUser(int UserID);
    public string ChannelName
    {
        get;
    }
}
