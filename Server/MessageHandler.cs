using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Networks;
public interface IMessageHandler<in T> where T : IMessage
{
    public void Handle([NotNull] T msg, MessageContext context);
}

public class MessageContext
{
    public MessageContext(IServer server, IMessageChannel channel)
    {
        Server = server;
        Channel = channel;
    }

    public IServer Server { get; init; }
    public IMessageChannel Channel { get; init; }
    public NetworkToken? ClientToken { get; init; }
}