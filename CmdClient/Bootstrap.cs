using System.Net;
using System.Net.Sockets;
using System.Text;

namespace ChattingRoom.CmdClient;
public class Bootstrap
{
    public static void Main(string[] vs)
    {
        Thread.Sleep(2000);
        IPAddress ip = IPAddress.Parse("127.0.0.1");
        int port = 5000;
        TcpClient client = new TcpClient();
        client.Connect(ip, port);
        Console.WriteLine("client connected!!");
        NetworkStream ns = client.GetStream();
        var thread = new Thread(() =>
        {
            NetworkStream ns = client.GetStream();
            byte[] receivedBytes = new byte[1024];
            int byte_count;

            while ((byte_count = ns.Read(receivedBytes, 0, receivedBytes.Length)) > 0)
            {
                Console.Write(Encoding.Unicode.GetString(receivedBytes, 0, byte_count));
            }
        });
        thread.Start();
    }
}
