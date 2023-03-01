namespace ChatRoom.Core.Network;
public interface IMessageChannelContainer {
    public IMessageChannel New(string channelName);
    public IMessageChannel? GetMessageChannelBy(string name);
}