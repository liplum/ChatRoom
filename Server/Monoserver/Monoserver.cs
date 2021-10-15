using ChattingRoom.Core;
using ChattingRoom.Core.Services;
using ChattingRoom.Core.Users;
using ChattingRoom.Server.Messages;
using ChattingRoom.Server.Networks;
using Room = ChattingRoom.Core.ChattingRoom;


namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly Room _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();
    private Network? _network;
    public INetwork? NetworkService
    {
        get => _network;
        private set
        {
            _network = (Network?)value;
        }
    }
    public IMessageChannel? User { get; private set; }

    public void Initialize()
    {
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
        _serviceContainer.RegisterInstance<INetwork>(new Network(this));
        NetworkService = _serviceContainer.Reslove<INetwork>();
    }
    public void Start()
    {
        if (NetworkService is null)
        {
            throw new NetworkServiceException();
        }
        NetworkService.StartService();
        InitChannels();
        InitUserService();
    }

    private void InitChannels()
    {
        InitUserChannel();
    }

    private void InitUserService()
    {
        if (NetworkService is null)
        {
            throw new NetworkServiceException();
        }
        NetworkService.OnClientConnected += token =>
        {
            User!.SendMessageToAll(new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
        };
    }

    private void InitUserChannel()
    {
        User = NetworkService!.New("User");
        User.RegisterMessageHandler<AuthenticationMsg, AuthenticationMsgHandler>("Authentication");
        User.RegisterMessage<RegisterResultMsg>("RegisterResult");
        User.RegisterMessage<RegisterRequestMsg>("RegisterRequest");
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
        return new UserID("test");
    }

    public IMessageChannel? GetMessageChannelBy(string name)
    {
        return null;
    }

    public bool Verify(UserID id, string password)
    {
        throw new NotImplementedException();
    }
}


[Serializable]
public class NetworkServiceException : Exception
{
    public NetworkServiceException() { }
    public NetworkServiceException(string message) : base(message) { }
    public NetworkServiceException(string message, Exception inner) : base(message, inner) { }
    protected NetworkServiceException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}