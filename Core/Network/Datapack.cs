namespace ChattingRoom.Core.Networks;
public class WriteableDatapack : IDatapack
{
    public WriteableDatapack()
    {
        Bytes = new(LengthPlaceholder);
    }
    public WriteableDatapack(IEnumerable<byte> data, bool insertByteArrayLengthAhead = true)
    {
        if (insertByteArrayLengthAhead)
        {
            Bytes = new List<byte>(LengthPlaceholder);
            Bytes.AddRange(data);
        }
        else
        {
            Bytes = new List<byte>(data);
        }
    }

    private static readonly byte[] LengthPlaceholder = new byte[] { 0, 0, 0, 0 };

    public WriteableDatapack(List<byte> data, bool insertByteArrayLengthAhead = true)
    {
        Bytes = data;
        if (insertByteArrayLengthAhead)
        {
            Bytes.InsertRange(0, LengthPlaceholder);
        }
    }

    private List<byte> Bytes
    {
        get; init;
    }

    public bool IsEmpty => Length == 0;

    public int Length => Bytes.Count;

    public bool CanWrite
    {
        get; private set;
    } = true;

    private bool _changed = false;

    public void Close()
    {
        CanWrite = false;
    }

    private byte[] _updated = Array.Empty<byte>();

    public void WriteInto([NotNull] Stream stream)
    {
        if (stream.CanWrite)
        {
            stream.Write(ToBytes());
        }
    }

    public byte[] ToBytes()
    {
        if (_changed)
        {
            Update();
        }
        return _updated;
    }

    private void Update()
    {
        var bytesLength = Bytes.Count - sizeof(int);
        var bytesLength_b = BitConverter.GetBytes(bytesLength);
        for (int i = 0; i < sizeof(int) && i < bytesLength_b.Length; i++)
        {
            Bytes[i] = bytesLength_b[i];
        }
        _updated = Bytes.ToArray();
    }

    private const string WhenDatapackClosed = "This datapack has been already closed.";

    public void Write(byte[] bytes)
    {
        if (!CanWrite)
        {
            throw new DatapackCantBeWrittenInException(WhenDatapackClosed);
        }
        if (bytes.Length > 0)
        {
            _changed = true;
            Bytes.AddRange(bytes);
        }
    }

    public void Write(ICollection<byte> bytes)
    {
        if (!CanWrite)
        {
            throw new DatapackCantBeWrittenInException(WhenDatapackClosed);
        }
        if (bytes.Count > 0)
        {
            _changed = true;
            Bytes.AddRange(bytes);
        }
    }

    public void Write(byte b)
    {
        if (!CanWrite)
        {
            throw new DatapackCantBeWrittenInException(WhenDatapackClosed);
        }
        _changed = true;
        Bytes.Add(b);
    }
}

public class ReadOnlyDatapck : IDatapack
{
    public ReadOnlyDatapck(byte[] data)
    {
        _bytes = data;
    }

    public readonly byte[] _bytes;

    public bool CanWrite => false;

    public bool IsEmpty => Length == 0;

    public int Length => _bytes.Length;

    public byte[] ToBytes()
    {
        return _bytes;
    }

    private const string WhenBeWrittenInExceptionMessage = "Read-only datapack can't be written in.";

    public void Write(byte[] bytes)
    {
        throw new DatapackCantBeWrittenInException(WhenBeWrittenInExceptionMessage);
    }

    public void WriteInto([NotNull] Stream stream)
    {
        if (stream.CanWrite)
        {
            stream.Write(BitConverter.GetBytes(_bytes.Length));
            stream.Write(_bytes);
        }
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
    public DatapackCantBeWrittenInException() { }
    public DatapackCantBeWrittenInException(string message) : base(message) { }
    public DatapackCantBeWrittenInException(string message, Exception inner) : base(message, inner) { }
    protected DatapackCantBeWrittenInException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}