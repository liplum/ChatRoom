using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IConnection //: IInjectable
{
    /*   public void SendMessageTo([NotNull] NetworkPositionToken target, byte[] data);

       public void SendMessageToAll(byte[] date);*/
    public void Send([NotNull] IDatapack datapack);

    public bool Connect();

    public bool Disconnect();

    public bool Terminal();

    public bool IsConnected { get; }
}

public class ConnectionClosedException:Exception{

}
