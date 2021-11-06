namespace ChattingRoom.Core.Users.Securities;
public struct Password
{
    private readonly string Md5Passwrod;
    public Password([NotNull] string md5)
    {
        Md5Passwrod = md5;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is Password o && string.Equals(Md5Passwrod, o.Md5Passwrod);
    }

    public static bool operator ==(Password left, Password right)
    {
        return left.Equals(right);
    }

    public static bool operator !=(Password left, Password right)
    {
        return !(left == right);
    }

    public override int GetHashCode()
    {
        return Md5Passwrod.GetHashCode();
    }
}