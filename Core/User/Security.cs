using System.Text;
using MD5Gener = System.Security.Cryptography.MD5;

namespace ChattingRoom.Core.Users.Securities;
public static class MD5
{
    private static readonly MD5Gener generator;
    static MD5()
    {
        generator = MD5Gener.Create();
    }
    public static string Convert(string password)
    {
        var inputBytes = Encoding.ASCII.GetBytes(password);
        var hash = generator.ComputeHash(inputBytes);
        var sb = new StringBuilder();
        for (var i = 0; i < hash.Length; i++)
        {
            sb.Append($"{hash[i]:x2}");
        }
        return sb.ToString();
    }

    public static bool Verify(string clearText, string md5Target)
    {
        var md5Pwd = Convert(clearText);
        return string.Equals(md5Pwd, md5Target);
    }
}

public static class Password
{
    public static bool IsValid(this string clear_password)
    {
        return true;
    }
}

public static class Account
{
    public static bool IsValid(this string account)
    {
        return true;
    }
}