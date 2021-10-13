using ChattingRoom.Server.Messages;

namespace ChattingRoom.Server;
public class Bootstrap
{
    public static void Main(string[] args)
    {
        var server = new Monoserver();
        server.Initialize();
        server.Start();
        Thread.Sleep(2000);
        server.User!.SendMessageToAll(new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
    }
}
