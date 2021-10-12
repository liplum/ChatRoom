namespace ChattingRoom.Server;
public class Bootstrap
{
    public static void Main(string[] args)
    {
        var server = new Monoserver();
        server.Initialize();
        server.Start();
    }
}
