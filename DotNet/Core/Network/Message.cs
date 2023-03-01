using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core.Ternimal;

namespace ChatRoom.Core.Network;

public interface IMessage
{
    public void Serialize(dynamic json);

    public void Deserialize(dynamic json);
}

public enum Direction
{
    ServerToClient,
    ClientToServer
}

[AttributeUsage(AttributeTargets.Class)]
public class MsgAttribute : Attribute
{
    public MsgAttribute(string id, params Direction[] direction)
    {
        Id = id;
        Direction = direction;
    }

    public MsgAttribute(params Direction[] direction)
    {
        Direction = direction;
    }

    public string? Id { get; init; }
    public Direction[] Direction { get; init; }

    public bool Accept(Direction direction)
    {
        return Direction.Contains(direction);
    }
}

public interface IMessageHandler<in T> where T : IMessage
{
    public void Handle([NotNull] T msg, MessageContext context);
}

public class MessageContext
{
    public MessageContext(INetwork network, IServer server, IMessageChannel channel)
    {
        Network = network;
        Server = server;
        Channel = channel;
    }

    public INetwork Network { get; }
    public IServer Server { get; }
    public IMessageChannel Channel { get; }
    public NetworkToken? ClientToken { get; init; }
}