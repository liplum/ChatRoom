using System.Text;

namespace ChatRoom.Core.Util;
public static class EncodeUtils {
    public static string ConvertToStringUnicode(byte[] b) {
        return Encoding.Unicode.GetString(b);
    }

    public static ICollection<byte> ConvertToBytesUnicode(string str) {
        return Encoding.Unicode.GetBytes(str);
    }

    public static string ConvertToStringWithLengthStartingUnicode(byte[] b) {
        using var stream = new MemoryStream(b);
        var buffer = new byte[sizeof(int)];
        stream.Read(buffer, 0, buffer.Length);
        var stringLength = BitConverter.ToInt32(buffer, 0);

        var bufferStr = new byte[sizeof(char) * stringLength];
        stream.Read(bufferStr, 0, bufferStr.Length);

        return ConvertToStringUnicode(bufferStr);
    }

    public static ICollection<byte> ConvertToBytesWithLengthStartingUnicode(string str) {
        var res = new List<byte>();
        var strLength = BitConverter.GetBytes(str.Length);
        res.AddRange(strLength);
        var content = ConvertToBytesUnicode(str);
        res.AddRange(content);
        return res;
    }

    public static byte[] MergeBytes(byte[] a, byte[] b) {
        var bytes = new byte[a.Length + b.Length];
        Buffer.BlockCopy(a, 0, bytes, 0, a.Length);
        Buffer.BlockCopy(b, 0, bytes, a.Length, b.Length);
        return bytes;
    }
}

public interface IBytesConverter {
    public string ConvertToString(byte[] b, bool startWithLength = true);

    public ICollection<byte> ConvertToBytes(string str, bool startWithLength = true);
}

public class UnicodeBytesConverter : IBytesConverter {
    public string ConvertToString(byte[] b, bool startWithLength = true) {
        if (startWithLength) return EncodeUtils.ConvertToStringWithLengthStartingUnicode(b);
        return EncodeUtils.ConvertToStringUnicode(b);
    }

    public ICollection<byte> ConvertToBytes(string str, bool startWithLength = true) {
        if (startWithLength) return EncodeUtils.ConvertToBytesWithLengthStartingUnicode(str);
        return EncodeUtils.ConvertToBytesUnicode(str);
    }
}