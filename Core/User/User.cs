using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Users;
public class User
{
    public User(UserInfo info)
    {
        Info = info;
    }

    public UserInfo Info
    {
        get; set;
    }

    public UserID ID
    {
        get => Info!.ID;
    }

    public NetworkToken? Token
    {
        get; set;
    }
}

public struct UserID
{
    public readonly string Name;
    public UserID(string name)
    {
        Name = name;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is UserID o && Name == o.Name;
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
        return Name.GetHashCode();
    }

    public static explicit operator string(UserID userId)
    {
        return userId.Name;
    }
    public static implicit operator UserID(string userId)
    {
        return new UserID(userId);
    }
}