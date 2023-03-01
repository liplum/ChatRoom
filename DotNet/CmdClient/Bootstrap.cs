using System.Net;
using System.Net.Sockets;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.CmdClient;
public static class Bootstrap {
    public static void Main(string[] vs) {
        Thread.Sleep(2000);
        var ip = IPAddress.Parse("127.0.0.1");
        const int port = 5000;
        var client = new TcpClient();
        client.Connect(ip, port);
        Console.WriteLine("client connected!!");
        var ns = client.GetStream();
        var thread = new Thread(() => {
            var stream = client.GetStream();
            var dataLengthBytes = new byte[sizeof(int)];
            const int intSize = sizeof(int);
            const int bufferSize = 1024;
            while (true)
                try {
                    stream.Read(dataLengthBytes, 0, intSize);
                    var dataLength = BitConverter.ToInt32(dataLengthBytes);
                    string res;
                    if (dataLength > bufferSize) {
                        var data = new List<byte>(dataLength);
                        var totalReadLength = 0;
                        while (true) {
                            var buffer = new byte[bufferSize];
                            var readLength = stream.Read(buffer, 0, buffer.Length);
                            totalReadLength += readLength;
                            var restLength = dataLength - totalReadLength;
                            if (restLength > bufferSize) {
                                data.AddRange(buffer);
                            }
                            else {
                                data.AddRange(buffer[..restLength]);
                                break;
                            }
                        }
                        var dataArray = data.ToArray();
                        res = EncodeUtils.ConvertToStringWithLengthStartingUnicode(dataArray);
                    }
                    else {
                        var data = new byte[dataLength];
                        stream.Read(data, 0, dataLength);
                        res = EncodeUtils.ConvertToStringWithLengthStartingUnicode(data);
                    }
                    Console.WriteLine(res);
                }
                catch {
                    break;
                }
        });
        thread.Start();
    }
}