using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public class WriteableDatapack : IDatapack
{
    public WriteableDatapack()
    {
        Bytes = new();
    }
    public WriteableDatapack(IEnumerable<byte> data)
    {
        Bytes = new List<byte>(data);
    }

    public WriteableDatapack(List<byte> data)
    {
        Bytes = data;
    }

    private List<byte> Bytes
    {
        get; init;
    }

    public bool IsEmpty => Length == 0;

    public int Length => Bytes.Count;

    public bool CanWrite => true;

    private bool _changed = false;

    private byte[] _updated = Array.Empty<byte>();

    public void WriteInto([NotNull] Stream stream)
    {
        if (stream.CanWrite)
        {
            stream.Write(BitConverter.GetBytes(Bytes.Count));
            stream.Write(Bytes.ToArray());
        }
    }

    public byte[] ToBytes()
    {
        if (_changed)
        {
            _updated = Bytes.ToArray();
        }
        return _updated;
    }

    public void Write(byte[] bytes)
    {
        if (bytes.Length > 0)
        {
            _changed = true;
            Bytes.AddRange(bytes);
        }
    }

    public void Write(byte b)
    {
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

    public void Write(byte[] bytes)
    {
        throw new NotSupportedException();
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
        throw new NotSupportedException();
    }
}