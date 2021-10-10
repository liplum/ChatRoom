namespace ChattingRoom.Core.Networks;
public interface IConnection //: IInjectable
{
    /*   public void SendMessageTo([NotNull] NetworkPositionToken target, byte[] data);

       public void SendMessageToAll(byte[] date);*/
    public void Send(IDatapack datapack);

    public bool Connect();

    public bool Disconnect();

    public bool IsConnected { get; }
}
