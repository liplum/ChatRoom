using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IDatapack
{
    public byte[] Bytes { get; }

    public bool IsEmpty { get; }

}

public class Datapack : IDatapack
{
    public static IDatapack Empty
    {
        get;
    } = new EmptyDatapack();

    public Datapack(byte[] data)
    {
        Bytes = data;
    }

    public byte[] Bytes
    {
        get; init;
    }

    public bool IsEmpty => Bytes.Length == 0;

    public static IDatapack ReadOne([NotNull] Stream stream)
    {
        if (!stream.CanRead)
        {
            return Empty;
        }
        const int IntSize = sizeof(int);
        var dataLength_Bytes = new byte[IntSize];
        try
        {
            stream.Read(dataLength_Bytes, 0, IntSize);
            int dataLength = BitConverter.ToInt32(dataLength_Bytes);
            var data = new byte[dataLength];
            stream.Read(data, 0, dataLength);
            return new Datapack(data);
        }
        catch (Exception)
        {
            return Empty;
        }
    }

    private class EmptyDatapack : IDatapack
    {
        public byte[] Bytes => Array.Empty<byte>();

        public bool IsEmpty => true;
    }
}