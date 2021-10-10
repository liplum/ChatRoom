using System.Text;

namespace ChattingRoom.Core;
public static class Utils
{
    public static string ConvertToStringUnicode(byte[] b)
    {
        return Encoding.Unicode.GetString(b);
    }
    public static byte[] ConvertToBytesUnicode(string str)
    {
        return Encoding.Unicode.GetBytes(str);
    }

    public static string ConvertToStringWithLengthBeginning(byte[] b)
    {
        using var stream = new MemoryStream(b);
        var buffer = new byte[sizeof(int)];
        stream.Read(buffer, 0, buffer.Length);
        int stringLength = BitConverter.ToInt32(buffer, 0);

        var bufferStr = new byte[sizeof(char) * stringLength];
        stream.Read(bufferStr, 0, bufferStr.Length);

        return ConvertToStringUnicode(bufferStr);
    }

    public static byte[] ConvertToBytesWithLengthBeginning(string str)
    {
        var strLength = BitConverter.GetBytes(str.Length);
        var content = ConvertToBytesUnicode(str);
        return MergeBytes(strLength, content);
    }

    public static byte[] MergeBytes(byte[] a, byte[] b)
    {
        var bytes = new byte[a.Length + b.Length];
        Buffer.BlockCopy(a, 0, bytes, 0, a.Length);
        Buffer.BlockCopy(b, 0, bytes, a.Length, b.Length);
        return bytes;
    }
}
public interface IBytesConverter
{
    public string ConvertToString(byte[] b);

    public byte[] ConvertToBytes(string str);
}
public class UnicodeBytesConverter : IBytesConverter
{
    public string ConvertToString(byte[] b) => Utils.ConvertToStringWithLengthBeginning(b);

    public byte[] ConvertToBytes(string str) => Utils.ConvertToBytesWithLengthBeginning(str);
}
