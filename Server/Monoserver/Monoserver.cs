global using System.Diagnostics.CodeAnalysis;
global using ChattingRoom.Core;
global using ChattingRoom.Core.Messages;
global using ChattingRoom.Core.Users;
global using ChattingRoom.Core.Utils;
global using ChatRoom = ChattingRoom.Core.DB.Models.ChattingRoom;
global using Membership = ChattingRoom.Core.DB.Models.Membership;
global using User = ChattingRoom.Core.DB.Models.User;
global using IServiceProvider = ChattingRoom.Core.IServiceProvider;
using System.Collections.Concurrent;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Services;
using ChattingRoom.Server.DB;
using ChattingRoom.Server.Interfaces;
using ChattingRoom.Server.Messages;
using ChattingRoom.Server.Services;
using static ChattingRoom.Core.IServer;

namespace ChattingRoom.Server;
public partial class Monoserver : IServer
{
#nullable disable
    private readonly ChatRoom _chatingRoom = new() { ChattingRoomID = 12345 };
    private readonly ServiceContainer _container = new()
    {
        HotReload = false
    };
    private Network _network;
    private Thread MainThread
    {
        get; set;
    }

    public IDatabase Database
    {
        get; set;
    }

    public event OnRegisterServiceHandler OnRegisterService;

    public INetwork NetworkService
    {
        get => _network;
        private set => _network = (Network)value;
    }
    public IMessageChannel User
    {
        get; private set;
    }
    public IMessageChannel Chatting
    {
        get; private set;
    }

    public ILogger Logger
    {
        get; private set;
    }
#nullable enable
    public IServiceProvider ServiceProvider => _container;

    public void Initialize()
    {
        _network = new Network(this);
        _container.RegisterSingleton<ILogger, CmdServerLogger>();
        _container.RegisterSingleton<IResourceManager, ResourceManager>();
        _container.RegisterSingleton<IUserService, UserService>();
        _container.RegisterSingleton<IChattingRoomService, ChattingRoomService>();
        _container.RegisterSingleton<IDatabase, Database>();

        _container.RegisterInstance<INetwork, Network>(_network);
        _container.RegisterInstance<IServer, Monoserver>(this);

        OnRegisterService?.Invoke(_container);

        _container.Close();

        NetworkService = _container.Reslove<INetwork>();
        Logger = _container.Reslove<ILogger>();
        Logger.StartService();
        Database = _container.Reslove<IDatabase>();
        Database.Connect();
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
            foreach (var task in ScheduledTask.GetConsumingEnumerable())
            {
                task?.Start();
            }
        });
        MainThread.Start();
    }

    private BlockingCollection<Task> ScheduledTask
    {
        get; init;
    } = new();


    public void AddScheduledTask([NotNull] Action task)
    {
        ScheduledTask.Add(new Task(task));
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
            AddScheduledTask(async () =>
            {
                Logger!.SendMessage($"{token.IpAddress} is connected and will be sent msg 10s soon.");
                await Task.Delay(10000);
                Chatting!.SendMessage(token, new ChattingMsg()
                {
                    ChattingRoomID = 12345,
                    Account = "System",
                    SendTime = DateTime.UtcNow,
                    ChattingText = "Hello user, welcome to the chatting room!"
                });
                Logger.SendMessage($"{token.IpAddress} was sent a msg from system.");
            });
        }
        !;
    }

    private void InitUserChannel()
    {
        User = NetworkService.New("User");
        User.RegisterMessage(() => new AuthenticationReqMsg(), () => new AuthenticationMsgHandler());
        User.RegisterMessage(() => new AuthenticationResultMsg());
        User.RegisterMessage(() => new RegisterResultMsg());
        User.RegisterMessage(() => new RegisterRequestMsg(), () => new RegisterRequestMsgHandler());

        Chatting = NetworkService.New("Chatting");
        Chatting.RegisterMessage(() => new ChattingMsg(), () => new ChattingMsgHandler());
    }

    public ChatRoom? GetChattingRoomBy(int chattingRoomID)
    {
        return _chatingRoom.ChattingRoomID == chattingRoomID ? _chatingRoom : null;
    }
}


[Serializable]
public class NetworkServiceException : Exception
{
    public NetworkServiceException()
    {
    }
    public NetworkServiceException(string message) : base(message) { }
    public NetworkServiceException(string message, Exception inner) : base(message, inner) { }
    protected NetworkServiceException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}