namespace ChatRoom.Server;
public static class Bootstrap {
    public static void Main(string[] args) {
        AppDomain.CurrentDomain.ProcessExit += OnQuit;
        Assets.InitConfigs();
        Assets.LoadConfigs();
        var server = new Monoserver.Monoserver();
        server.Initialize();
        server.Start();
    }

    private static void OnQuit(object? sender, EventArgs e) {
        Assets.SaveConfig();
    }
}