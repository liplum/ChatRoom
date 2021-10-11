using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IDatapack
{
    public byte[] Bytes { get; }

    public bool IsEmpty { get; }

    public void WriteInto([NotNull] Stream stream);
}

public class Datapack : IDatapack
{
    public static IDatapack Empty
    {
        get;
    } = new EmptyDatapack();

    public Datapack(byte[] data)
    {
        _bytes = data;
    }

    private bool Initialized
    {
        get; set;
    } = false;

    public readonly byte[] _bytes;
    public byte[]? _initialized;
    public byte[] Bytes
    {
        get
        {
            if (!Initialized)
            {
                _initialized = new byte[_bytes.Length + sizeof(int)];
                var bytes = new ReadOnlySpan<byte>(_bytes);
                var initiliazed = new Span<byte>(_initialized, sizeof(int), _initialized.Length);
                bytes.CopyTo(initiliazed);
                Initialized = true;
            }
            return _initialized ?? Array.Empty<byte>();
        }
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

    public static IDatapack GenLazyEvaluation(WriteInto writeInto)
    {

    }

    private class LazyEvaluatedDatapack : IDatapack
    {
        private readonly WriteInto _writeInto;
        public LazyEvaluatedDatapack(WriteInto writeInto)
        {
            _writeInto = writeInto;
        }

        public byte[] Bytes
        {
            get
            {
                using var s = new MemoryStream();
                _writeInto(s);
                return ReadOne(s).Bytes;
            }
        }

        public bool IsEmpty => false;

        public void WriteInto([NotNull] Stream stream)
        {
            _writeInto(stream);
        }
    }

    public void WriteInto([NotNull] Stream stream)
    {
        if (stream.CanWrite)
        {
            stream.Write(BitConverter.GetBytes(_bytes.Length));
            stream.Write(_bytes);
        }
    }

    private class EmptyDatapack : IDatapack
    {
        public byte[] Bytes => Array.Empty<byte>();

        public bool IsEmpty => true;

        public void WriteInto([NotNull] Stream stream)
        {

        }
    }
}

public delegate byte[] GetBytes(byte[] rawData);
public delegate void WriteInto(Stream stream);