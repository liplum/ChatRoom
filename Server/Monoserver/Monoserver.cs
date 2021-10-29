using ChattingRoom.Core;
using ChattingRoom.Core.Messages;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Core.Users;
using ChattingRoom.Server.Messages;
using System.Diagnostics.CodeAnalysis;
using static ChattingRoom.Core.IServer;
using Room = ChattingRoom.Core.ChattingRoom;


namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly Room _chatingRoom = new();
    private readonly ServiceContainer _serviceContainer = new();
    private Network? _network;
    private Thread? MainThread
    {
        get; set;
    }

    public event OnRegisterServiceHandler? OnRegisterService;

    public INetwork? NetworkService
    {
        get => _network;
        private set
        {
            _network = (Network?)value;
        }
    }
    public IMessageChannel? User { get; private set; }

    public ILogger? Logger { get; private set; }

    public void Initialize()
    {
        _network = new Network(this);
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
        _serviceContainer.RegisterInstance<INetwork, Network>(_network);
        OnRegisterService?.Invoke(_serviceContainer);
        NetworkService = _serviceContainer.Reslove<INetwork>();
        Logger = _serviceContainer.Reslove<ILogger>();
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
        StartMainThread();
    }

    private void StartMainThread()
    {
        MainThread = new Thread(() =>
        {
            while (true)
            {
                lock (_mainThreadLock)
                {
                    while (ScheduledTask.TryDequeue(out var task))
                    {
                        task.Start();
                    }
                }
            }
        });
        MainThread.Start();
    }

    private Queue<Task<Action>> ScheduledTask
    {
        get; init;
    } = new();

    private readonly object _mainThreadLock = new();

    public void AddScheduledTask([NotNull] Task<Action> action)
    {
        lock (_mainThreadLock)
        {
            ScheduledTask.Enqueue(action);
        }
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
        NetworkService.OnClientConnected += async token =>
        {
            Logger!.SendMessage($"{token.IpAddress} is connected and will be sent msg 3s soon.");
            await Task.Delay(3000);//3 secs
            User!.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
            Logger.SendMessage($"{token.IpAddress} was sent a msg.");
        };
    }

    private void InitUserChannel()
    {
        User = NetworkService!.New("User");
        User.RegisterMessageHandler<AuthenticationMsg, AuthenticationMsgHandler>();
        User.RegisterMessage<RegisterResultMsg>();
        User.RegisterMessage<RegisterRequestMsg>();
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