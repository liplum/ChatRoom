using System.Net;

namespace ChatRoom.Core.Network;

public class NetworkToken
{
    public NetworkToken(IPAddress ipAddress)
    {
        IpAddress = ipAddress;
    }

    public IPAddress IpAddress { get; init; }

    public override string ToString()
    {
        return IpAddress.ToString();
    }
}