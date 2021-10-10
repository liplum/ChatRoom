using ChattingRoom.Core;
using System.Diagnostics.CodeAnalysis;
using IServiceProvider = ChattingRoom.Core.IServiceProvider;

namespace ChattingRoom.Server.Services;
public class CmdServerLogger : ILogger
{
    public void Log([NotNull] WarnningLevel level, string message)
    {
        ApplyColor(level);
        Console.WriteLine($"{DateTime.Now:yyyyMMdd-HH:mm:ss}[{level}]{message}");
        ClearColor();
    }

    private static void ApplyColor([NotNull] WarnningLevel level)
    {
        switch (level)
        {
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

    private static void ClearColor()
    {
        Console.ForegroundColor = ConsoleColor.White;
    }

    public void Initialize(IServiceProvider serviceProvider)
    {

    }
}
