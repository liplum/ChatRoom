namespace ChattingRoom.Core.Networks;
public interface IConnection //: IInjectable
{
    /// <summary>
    /// 
    /// </summary>
    /// <param name="datapack"></param>
    /// <exception cref="ConnectionClosedException">Raised if the connection had been already closed.</exception>
    public void Send([NotNull] IDatapack datapack);

    public bool Connect();

    public bool Disconnect();

    public bool Terminal();

    public bool IsConnected { get; }
}

[Serializable]
public class ConnectionClosedException : Exception
{
    public ConnectionClosedException() { }
    public ConnectionClosedException(string message) : base(message) { }
    public ConnectionClosedException(string message, Exception inner) : base(message, inner) { }
    protected ConnectionClosedException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}