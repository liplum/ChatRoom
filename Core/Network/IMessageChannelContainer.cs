namespace ChattingRoom.Core.Networks;
public interface IMessageChannelContainer
{
    public IMessageChannel New(string channelName);
}
