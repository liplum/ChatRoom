using ChattingRoom.Core;
using ChattingRoom.Core.Services;
using ChattingRoom.Server.Messages;
using ChattingRoom.Server.Networks;
using Room = ChattingRoom.Core.ChattingRoom;


namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly Room _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();
    private Network? _network;
    public IMessageChannel? User { get; private set; }

    public void Initialize()
    {
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
        _serviceContainer.RegisterInstance<INetwork>(new Network(this));
        _network = (Network?)_serviceContainer.Reslove<INetwork>();
    }
    public void Start()
    {
        _network!.StartService();
        InitChannels();
    }

    private void InitChannels()
    {
        InitUserChannel();
    }

    private void InitUserChannel()
    {
        User = _network!.New("User");
        User.RegisterMessageType<AuthenticationMsg, AuthenticationMsgHandler>("Authentication");
        User.RegisterMessageType<RegisterResultMsg>("RegisterResult");
    }

    public Room? GetChattingRoomBy(ChattingRoomID ID)
    {
        return _chatingRoom.ID == ID ? _chatingRoom : null;
    }

    public void RegisterUser(UserID userID)
    {

    }

    public UserID GenAvailableUserID()
    {
        return new UserID(12345);
    }

    public IMessageChannel? GetMessageChannelBy(string name)
    {
        return null;
    }
}
