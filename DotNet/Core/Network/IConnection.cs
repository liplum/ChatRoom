using System.Runtime.Serialization;

namespace ChatRoom.Core.Network;

public interface IConnection //: IInjectable
{
    public bool IsConnected { get; }

    /// <summary>
    /// </summary>
    /// <param name="datapack"></param>
    /// <exception cref="ConnectionClosedException">Raised if the connection had been already closed.</exception>
    public void Send(IDatapack datapack);

    public bool Connect();

    public bool Disconnect();

    public bool Terminal();
}

[Serializable]
public class ConnectionClosedException : Exception
{
    public ConnectionClosedException()
    {
    }

    public ConnectionClosedException(string message) : base(message)
    {
    }

    public ConnectionClosedException(string message, Exception inner) : base(message, inner)
    {
    }

    protected ConnectionClosedException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}