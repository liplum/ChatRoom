using ChattingRoom.Core.Utils;
using System.Net;
using System.Net.Sockets;

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
            NetworkStream stream = client.GetStream();
            byte[] dataLength_Bytes = new byte[sizeof(int)];
            var IntSize = sizeof(int);
            var bufferSize = 1024;
            string res = "";
            while (true)
            {
                try
                {
                    stream.Read(dataLength_Bytes, 0, IntSize);
                    int dataLength = BitConverter.ToInt32(dataLength_Bytes);
                    if (dataLength > bufferSize)
                    {
                        var data = new List<byte>(dataLength);
                        int totalReadLength = 0;
                        while (true)
                        {
                            var buffer = new byte[bufferSize];
                            int readLength = stream.Read(buffer, 0, buffer.Length);
                            totalReadLength += readLength;
                            int restLength = dataLength - totalReadLength;
                            if (restLength > bufferSize)
                            {
                                data.AddRange(buffer);
                            }
                            else
                            {
                                data.AddRange(buffer[0..restLength]);
                                break;
                            }
                        }
                        var dataArray = data.ToArray();
                        res = EncodeUtils.ConvertToStringWithLengthStartingUnicode(dataArray);
                    }
                    else
                    {
                        var data = new byte[dataLength];
                        stream.Read(data, 0, dataLength);
                        res = EncodeUtils.ConvertToStringWithLengthStartingUnicode(data);
                    }
                    Console.WriteLine(res);
                }
                catch
                {
                    break;
                }
            }
        });
        thread.Start();
    }
}
