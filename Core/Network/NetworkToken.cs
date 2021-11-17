using System.Net;

namespace ChattingRoom.Core.Networks;
public class NetworkToken
{
    public NetworkToken(IPAddress ipAddress)
    {
        IpAddress = ipAddress;
    }
    public IPAddress IpAddress
    {
        get; init;
    }

    public override string ToString()
    {
        return IpAddress.ToString();
    }
}
