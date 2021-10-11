using ChattingRoom.Core;
using ChattingRoom.Core.Services;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly ChatingRoom _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();

    public void Initialize()
    {
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
    }
}
