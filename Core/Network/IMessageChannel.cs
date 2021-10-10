using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IMessageChannel
{
    public void SendMessage([NotNull] NetworkToken target, [NotNull] IMessage msg);
    public void SendMessageToAll([NotNull] IMessage msg);

    public string ChannelName
    {
        get;
    }

    public ChannelDirection ChannelDirection
    {
        get;
    }
}

public enum ChannelDirection
{
    ServerToClient, ClientToServer
}