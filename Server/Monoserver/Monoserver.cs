using ChattingRoom.Core;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly ChattingRoom _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();
    private 
    private Network? _network;

    public void Initialize()
    {
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
        _serviceContainer.RegisterInstance<INetwork>(new Network(this));
        _network = (Network?)_serviceContainer.Reslove<INetwork>();
    }

    public void Start()
    {
        _network!.StartService();
    }
    public ChattingRoom? GetChattingRoomBy(ChattingRoomID ID)
    {
        return _chatingRoom.ID == ID ? _chatingRoom : null;
    }
    public bool RegisterUser(int UserID){

    }
}
