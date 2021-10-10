using System.Net;
using System.Net.Sockets;
using System.Text;

namespace ChattingRoom.Server;
public class Program
{
    public static readonly object _lock = new();
    public static readonly Dictionary<int, TcpClient> _allClients = new();

    public static void Main(string[] args)
    {
        int count = 1;

        TcpListener ServerSocket = new TcpListener(IPAddress.Any, 5000);
        ServerSocket.Start();

        var autoKick = new Thread(() =>
        {
            var r = Random.Shared;
            while (true)
            {
                Thread.Sleep(15000);
                var keys = _allClients.Keys;
                if (keys.Count > 0)
                {
                    var number = keys.ElementAt(r.Next(keys.Count));
                    Console.WriteLine($"[{number}] will be kicked soon.");
                    KickClient(_allClients[number]);
                }
            }

        });
        autoKick.Start();

        while (true)
        {
            TcpClient client = ServerSocket.AcceptTcpClient();
            lock (_lock) _allClients.Add(count, client);
            Console.WriteLine("Someone connected!!");

            int id = count;
            Thread t = new Thread(() =>
            {
                TcpClient client;

                lock (_lock) client = _allClients[id];

                while (true)
                {
                    if (!client.Connected)
                    {
                        break;
                    }
                    NetworkStream stream = client.GetStream();
                    byte[] buffer = new byte[1024];
                    try
                    {
                        int byte_count = stream.Read(buffer, 0, buffer.Length);
                        if (byte_count == 0)
                        {
                            break;
                        }
                        string data = Encoding.ASCII.GetString(buffer, 0, byte_count);
                        Broadcast(id, data);
                        Console.WriteLine(data);
                    }
                    catch (Exception)
                    {
                        break;
                    }
                }
                lock (_lock) _allClients.Remove(id);
                if (client.Connected)
                {
                    client.Client.Shutdown(SocketShutdown.Both);
                    KickClient(client);
                }
                Console.WriteLine($"[{id}] disconncted.");
            });
            t.Start();
            count++;
        }
    }

    public static void KickClient(TcpClient client)
    {
        client.Close();
    }

    public static void Broadcast(int id, string data)
    {
        byte[] buffer = Encoding.ASCII.GetBytes($"[{id}]{data}{Environment.NewLine}");

        lock (_lock)
        {
            foreach (TcpClient c in _allClients.Values)
            {
                NetworkStream stream = c.GetStream();

                stream.Write(buffer, 0, buffer.Length);
            }
        }
    }
}