﻿namespace ChatRoom.Core.Network;

public interface IDatapack
{
    public bool CanWrite { get; }

    public bool IsEmpty { get; }

    public int Length { get; }
    public byte[] ToBytes();
    public void Write(byte[] bytes);
    public void Write(ICollection<byte> bytes);

    public void Write(byte b);

    public void WriteInto(Stream stream);
}

public static class Datapack
{
    public static IDatapack Empty { get; } = new EmptyDatapack();

    public static IDatapack ReadOne(Stream stream, int bufferSize = 1024)
    {
        if (!stream.CanRead) return Empty;
        const int intSize = sizeof(int);
        var dataLengthBytes = new byte[intSize];
        try
        {
            stream.Read(dataLengthBytes, 0, intSize);
            var dataLength = BitConverter.ToInt32(dataLengthBytes);
            if (dataLength > bufferSize)
            {
                var data = new List<byte>(dataLength);
                var totalReadLength = 0;
                while (true)
                {
                    var buffer = new byte[bufferSize];
                    var readLength = stream.Read(buffer, 0, buffer.Length);
                    totalReadLength += readLength;
                    var restLength = dataLength - totalReadLength;
                    if (restLength > bufferSize)
                    {
                        data.AddRange(buffer);
                        restLength -= bufferSize;
                    }
                    else
                    {
                        data.AddRange(buffer[..restLength]);
                        break;
                    }
                }

                return new ReadOnlyDatapack(data.ToArray());
            }
            else
            {
                var data = new byte[dataLength];
                stream.Read(data, 0, dataLength);
                return new ReadOnlyDatapack(data);
            }
        }
        catch (Exception)
        {
            return Empty;
        }
    }

    public static IDatapack Write(this IDatapack datapack, int data)
    {
        datapack.Write(BitConverter.GetBytes(data));
        return datapack;
    }

    public static IDatapack Write(this IDatapack datapack, short data)
    {
        datapack.Write(BitConverter.GetBytes(data));
        return datapack;
    }

    public static IDatapack Write(this IDatapack datapack, long data)
    {
        datapack.Write(BitConverter.GetBytes(data));
        return datapack;
    }

    public static IDatapack Write(this IDatapack datapack, float data)
    {
        datapack.Write(BitConverter.GetBytes(data));
        return datapack;
    }

    public static IDatapack Write(this IDatapack datapack, double data)
    {
        datapack.Write(BitConverter.GetBytes(data));
        return datapack;
    }

    private class EmptyDatapack : IDatapack
    {
        public bool IsEmpty => true;

        public int Length => 0;

        public bool CanWrite => throw new NotImplementedException();

        public byte[] ToBytes()
        {
            return Array.Empty<byte>();
        }

        public void Write(byte[] bytes)
        {
        }

        public void Write(byte b)
        {
        }

        public void Write(ICollection<byte> bytes)
        {
        }

        public void WriteInto(Stream stream)
        {
        }
    }
}