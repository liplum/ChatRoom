namespace ChattingRoom.Core.Networks;
public interface IMessageHandler<in T> where T : IMessage {
    public void Handle([NotNull] T msg, MessageContext context);
}

public class MessageContext {
    public MessageContext(INetwork network,IServer server, IMessageChannel channel) {
        Network = network;
        Server = server;
        Channel = channel;
    }
    public INetwork Network { get; }
    public IServer Server { get; }
    public IMessageChannel Channel { get; }
    public NetworkToken? ClientToken { get; init; }
}