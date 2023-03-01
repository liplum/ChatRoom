using System.Collections.Concurrent;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Services;
public class CmdServerLogger : ILogger {
    private readonly object _lock = new();
#nullable disable
    private IResourceManager ResourceManager {
        get;
        set;
    }
#nullable enable
    private Thread? MainThread {
        get;
        set;
    }
    private StreamWriter? LogFile {
        get;
        set;
    }
    private BlockingCollection<(WarnningLevel, string)> Logs {
        get;
    } = new();
    public void Log(WarnningLevel level, string message) {
        Logs.Add((level, message));
    }
    public void StartService() {
        var today = DateTime.Today;
        Directory.CreateDirectory(ResourceManager.LogsFolder);
        LogFile = new($"{ResourceManager.LogsFolder}/{today:yyyyMMdd}.log", true) {
            AutoFlush = true
        };
        MainThread = new(() => {
            foreach (var (level, msg) in Logs.GetConsumingEnumerable()) {
                var log = $"{DateTime.Now:yyyyMMdd-HH:mm:ss}[{level}]{msg}";
                LogFile?.WriteLine(log);
                ApplyColor(level);
                Console.WriteLine(log);
                Console.Out.Flush();
                ClearColor();
            }
        });
        MainThread.Start();
    }

    public void StopService() {
        Logs.CompleteAdding();
        MainThread?.Interrupt();
        LogFile?.Close();
    }

    private static void ApplyColor(WarnningLevel level) {
        switch (level) {
            case WarnningLevel.Message:
                Console.ForegroundColor = ConsoleColor.White;
                break;
            case WarnningLevel.Tip:
                Console.ForegroundColor = ConsoleColor.Blue;
                break;
            case WarnningLevel.Warn:
                Console.ForegroundColor = ConsoleColor.Yellow;
                break;
            case WarnningLevel.Error:
                Console.ForegroundColor = ConsoleColor.Red;
                break;
        }
    }

    private static void ClearColor() {
        Console.ForegroundColor = ConsoleColor.White;
    }

    public void Initialize(IServiceProvider serviceProvider) {
        ResourceManager = serviceProvider.Resolve<IResourceManager>();
    }
}