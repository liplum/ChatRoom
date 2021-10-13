using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core;
public class User
{

}

public struct UserID
{
    private readonly int ID;
    public UserID(int id)
    {
        ID = id;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is UserID o && ID == o.ID;
    }

    public static bool operator ==(UserID left, UserID right)
    {
        return left.Equals(right);
    }

    public static bool operator !=(UserID left, UserID right)
    {
        return !(left == right);
    }

    public override int GetHashCode()
    {
        return ID.GetHashCode();
    }
}
