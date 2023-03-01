namespace ChatRoom.Core.Network;
public interface IMessage {
    public void Serialize(dynamic json);

    public void Deserialize(dynamic json);
}

public enum Direction {
    ServerToClient, ClientToServer
}

[AttributeUsage(AttributeTargets.Class)]
public class MsgAttribute : Attribute {
    public MsgAttribute(string id, params Direction[] direction) {
        Id = id;
        Direction = direction;
    }

    public MsgAttribute(params Direction[] direction) {
        Direction = direction;
    }
    public string? Id {
        get;
        init;
    }
    public Direction[] Direction {
        get;
        init;
    }

    public bool Accept(Direction direction) {
        return Direction.Contains(direction);
    }
}