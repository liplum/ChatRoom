using System.Runtime.Serialization;

namespace ChatRoom.Core.Network;

public class WriteableDatapack : IDatapack
{
    private const string WhenDatapackClosed = "This datapack has been already closed.";

    private static readonly byte[] LengthPlaceholder = { 0, 0, 0, 0 };

    private bool _changed;

    private byte[] _updated = Array.Empty<byte>();

    public WriteableDatapack()
    {
        Bytes = new(LengthPlaceholder);
    }

    public WriteableDatapack(IEnumerable<byte> data, bool insertByteArrayLengthAhead = true)
    {
        if (insertByteArrayLengthAhead)
        {
            Bytes = new(LengthPlaceholder);
            Bytes.AddRange(data);
        }
        else
        {
            Bytes = new(data);
        }
    }

    public WriteableDatapack(List<byte> data, bool insertByteArrayLengthAhead = true)
    {
        Bytes = data;
        if (insertByteArrayLengthAhead) Bytes.InsertRange(0, LengthPlaceholder);
    }

    private List<byte> Bytes { get; }

    public bool IsEmpty => Length == 0;

    public int Length => Bytes.Count;

    public bool CanWrite { get; private set; } = true;

    public void WriteInto(Stream stream)
    {
        if (stream.CanWrite) stream.Write(ToBytes());
    }

    public byte[] ToBytes()
    {
        if (_changed) Update();

        return _updated;
    }

    public void Write(byte[] bytes)
    {
        if (!CanWrite) throw new DatapackCantBeWrittenInException(WhenDatapackClosed);

        if (bytes.Length <= 0) return;
        _changed = true;
        Bytes.AddRange(bytes);
    }

    public void Write(ICollection<byte> bytes)
    {
        if (!CanWrite) throw new DatapackCantBeWrittenInException(WhenDatapackClosed);

        if (bytes.Count <= 0) return;
        _changed = true;
        Bytes.AddRange(bytes);
    }

    public void Write(byte b)
    {
        if (!CanWrite) throw new DatapackCantBeWrittenInException(WhenDatapackClosed);

        _changed = true;
        Bytes.Add(b);
    }

    public void Close()
    {
        CanWrite = false;
    }

    private void Update()
    {
        var bytesLength = Bytes.Count - sizeof(int);
        var bytesLengthB = BitConverter.GetBytes(bytesLength);
        for (var i = 0; i < sizeof(int) && i < bytesLengthB.Length; i++) Bytes[i] = bytesLengthB[i];

        _updated = Bytes.ToArray();
    }
}

public class ReadOnlyDatapack : IDatapack
{
    private const string WhenBeWrittenInExceptionMessage = "Read-only datapack can't be written in.";

    public readonly byte[] Bytes;

    public ReadOnlyDatapack(byte[] data)
    {
        Bytes = data;
    }

    public bool CanWrite => false;

    public bool IsEmpty => Length == 0;

    public int Length => Bytes.Length;

    public byte[] ToBytes()
    {
        return Bytes;
    }

    public void Write(byte[] bytes)
    {
        throw new DatapackCantBeWrittenInException(WhenBeWrittenInExceptionMessage);
    }

    public void WriteInto(Stream stream)
    {
        if (!stream.CanWrite) return;
        stream.Write(BitConverter.GetBytes(Bytes.Length));
        stream.Write(Bytes);
    }

    public void Write(byte b)
    {
        throw new DatapackCantBeWrittenInException(WhenBeWrittenInExceptionMessage);
    }

    public void Write(ICollection<byte> bytes)
    {
        throw new DatapackCantBeWrittenInException(WhenBeWrittenInExceptionMessage);
    }
}

[Serializable]
public class DatapackCantBeWrittenInException : Exception
{
    public DatapackCantBeWrittenInException()
    {
    }

    public DatapackCantBeWrittenInException(string message) : base(message)
    {
    }

    public DatapackCantBeWrittenInException(string message, Exception inner) : base(message, inner)
    {
    }

    protected DatapackCantBeWrittenInException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}