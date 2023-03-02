using System.Collections.Concurrent;
using ChatRoom.Core.Interface;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Services;

public class CmdServerLoggerManager : ILoggerManager
{
#nullable disable
    private IResourceManager ResourceManager { get; set; }
#nullable enable
    private Thread? MainThread { get; set; }
    private StreamWriter? LogFile { get; set; }
    private BlockingCollection<(DateTime, WarnningLevel, string)> Logs { get; } = new();

    public void Log(WarnningLevel level, string message)
    {
        Logs.Add((DateTime.Now, level, message));
    }

    public ILogger OnSubChannel(string channelName)
    {
        return new SubChannelLogger(this, channelName);
    }

    public void StartService()
    {
        var today = DateTime.Today;
        Directory.CreateDirectory(ResourceManager.LogsFolder);
        LogFile = new($"{ResourceManager.LogsFolder}/{today:yyyyMMdd}.log", true)
        {
            AutoFlush = true
        };
        MainThread = new(() =>
        {
            foreach (var (time, level, msg) in Logs.GetConsumingEnumerable())
            {
                var log = $"{time:HH:mm:ss}[{level}]{msg}";
                LogFile?.WriteLine(log);
                ApplyColor(level);
                Console.WriteLine(log);
                Console.Out.Flush();
                ClearColor();
            }
        });
        MainThread.Start();
    }

    public void StopService()
    {
        Logs.CompleteAdding();
        MainThread?.Interrupt();
        LogFile?.Close();
    }


    private static void ApplyColor(WarnningLevel level)
    {
        Console.ForegroundColor = level switch
        {
            WarnningLevel.Message => ConsoleColor.White,
            WarnningLevel.Tip => ConsoleColor.Blue,
            WarnningLevel.Warn => ConsoleColor.Yellow,
            WarnningLevel.Error => ConsoleColor.Red,
            _ => Console.ForegroundColor
        };
    }

    private static void ClearColor()
    {
        Console.ForegroundColor = ConsoleColor.White;
    }

    public void Initialize(IServiceProvider serviceProvider)
    {
        ResourceManager = serviceProvider.Resolve<IResourceManager>();
    }
}

internal class SubChannelLogger : ILogger
{
    private readonly ILogger? _parent;
    private readonly string? _channelName;

    public SubChannelLogger(ILogger parent, string channelName)
    {
        _parent = parent;
        _channelName = channelName;
    }

    public void Log(WarnningLevel level, string message)
    {
        if (_parent is not null && _channelName is not null)
        {
            _parent.Log(level, $"[{_channelName}]{message}");
        }
    }

    public ILogger OnSubChannel(string channelName)
    {
        return new SubChannelLogger(this, channelName);
    }
}