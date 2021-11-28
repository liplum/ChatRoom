using System.Text;
using System.Text.RegularExpressions;
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

    public static string Encrypted(this string clearPassword)
    {
        var md5Pwd = Convert(clearPassword);
        var md5Twice = Convert(md5Pwd);
        return Convert(md5Twice);
    }

    public static bool Verify(string clearPassword, string md5Target)
    {
        return string.Equals(clearPassword.Encrypted(), md5Target);
    }
}

public static class Password
{
    public static readonly Regex PasswordRegex = new(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$");

    public static bool IsValid(this string clear_password)
    {
        if (string.IsNullOrEmpty(clear_password))
        {
            return false;
        }
        return PasswordRegex.IsMatch(clear_password);
    }
}

public static class Account
{
    public static readonly Regex AccountRegex = new(@"^[a-zA-Z0-9_]{3,16}$");
    public static bool IsValid(this string account)
    {
        if (string.IsNullOrEmpty(account))
        {
            return false;
        }
        return AccountRegex.IsMatch(account);
    }
}