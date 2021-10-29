using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core;
public class ChattingRoom
{

    public ChattingRoomID ID
    {
        get; set;
    }
}


public struct ChattingRoomID
{
    private readonly int ID;
    public ChattingRoomID(int id)
    {
        ID = id;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is ChattingRoomID o && ID == o.ID;
    }

    public static bool operator ==(ChattingRoomID left, ChattingRoomID right)
    {
        return left.Equals(right);
    }

    public static bool operator !=(ChattingRoomID left, ChattingRoomID right)
    {
        return !(left == right);
    }

    public override int GetHashCode()
    {
        return ID.GetHashCode();
    }
}