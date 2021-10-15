namespace ChattingRoom.Core.Networks;
public interface IMessage
{
    public void Serialize(dynamic json);

    public void Deserialize(dynamic json);
}

public enum Direction
{
    ServerToClient, ClientToServer
}

[AttributeUsage(AttributeTargets.Class, Inherited = false, AllowMultiple = false)]
public sealed class DirectionAttribute : Attribute
{
    public Direction[] Direction
    {
        get; init;
    }

    public DirectionAttribute(params Direction[] directions)
    {
        if (directions.Length == 0)
        {
            throw new ArgumentException("Direction given is none.");
        }
        Direction = directions;
    }

    public bool Accept(Direction direction)
    {
        return Direction.Contains(direction);
    }
}