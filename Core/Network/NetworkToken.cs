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

    public override bool Equals(object? obj)
    {
        return obj is NetworkToken o
            && this.IpAddress.Equals(o.IpAddress);
    }

    public override int GetHashCode()
    {
        return IpAddress.GetHashCode();
    }
}
