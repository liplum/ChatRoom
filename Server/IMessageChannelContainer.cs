namespace ChattingRoom.Server.Networks;
public interface IMessageChannelContainer
{
    public IMessageChannel New(string channelName);
}
