using ChattingRoom.Core;
using ChattingRoom.Core.Message;
using ChattingRoom.Core.Messages;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Core.User;
using ChattingRoom.Server.Messages;
using System.Diagnostics.CodeAnalysis;
using static ChattingRoom.Core.IServer;
using Room = ChattingRoom.Core.ChattingRoom;


namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
    private readonly Room _chatingRoom = new() { ID = new(12345) };
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
    public IMessageChannel? Chatting { get; private set; }

    public ILogger? Logger { get; private set; }

    public void Initialize()
    {
        _network = new Network(this);
        _serviceContainer.RegisterSingleton<ILogger, CmdServerLogger>();
        _serviceContainer.RegisterInstance<INetwork, Network>(_network);
        _serviceContainer.RegisterInstance<IServer, Monoserver>(this);
        _serviceContainer.RegisterSingleton<IUserService, UserService>();

        OnRegisterService?.Invoke(_serviceContainer);

        NetworkService = _serviceContainer.Reslove<INetwork>();
        Logger = _serviceContainer.Reslove<ILogger>();
        UserService = _serviceContainer.Reslove<IUserService>();
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
        _serviceContainer.Inject(_chatingRoom);
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

    private Queue<Task> ScheduledTask
    {
        get; init;
    } = new();

    public IUserService? UserService { get; private set; }

    private readonly object _mainThreadLock = new();

    public void AddScheduledTask([NotNull] Action task)
    {
        lock (_mainThreadLock)
        {
            ScheduledTask.Enqueue(new Task(task));
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
            Logger!.SendMessage($"{token.IpAddress} is connected and will be sent msg 20s soon.");
            await Task.Delay(20000);
            User!.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
            Logger.SendMessage($"{token.IpAddress} was sent a msg.");
        };

        NetworkService.OnClientConnected += async token =>
        {
            Logger!.SendMessage($"{token.IpAddress} is connected and will be sent msg 10s soon.");
            await Task.Delay(10000);
            Chatting!.SendMessage(token, new ChattingMsg()
            {
                ChattingRoomID = 12345,
                UserID = "System",
                SendTime = DateTime.UtcNow,
                ChattingText = "From System!!!"
            });
            Logger.SendMessage($"{token.IpAddress} was sent a msg from system.");
        };
    }

    private void InitUserChannel()
    {
        User = NetworkService!.New("User");
        User.RegisterMessageHandler<AuthenticationMsg, AuthenticationMsgHandler>();
        User.RegisterMessage<RegisterResultMsg>();
        User.RegisterMessage<RegisterRequestMsg>();

        Chatting = NetworkService!.New("Chatting");
        Chatting.RegisterMessageHandler<ChattingMsg, ChattingMsgHandler>();
    }

    public Room? GetChattingRoomBy(ChattingRoomID ID)
    {
        return _chatingRoom.ID == ID ? _chatingRoom : null;
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