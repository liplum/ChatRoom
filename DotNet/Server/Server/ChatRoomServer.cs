global using IServiceProvider = ChatRoom.Core.Interface.IServiceProvider;
using System.Collections.Concurrent;
using System.Runtime.Serialization;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Network;
using ChatRoom.Core.Service;
using ChatRoom.Core.Ternimal;
using ChatRoom.Server.Interfaces;
using ChatRoom.Server.MessageHandler;
using ChatRoom.Server.Services;
using static ChatRoom.Core.Ternimal.IServer;

namespace ChatRoom.Server;

public partial class ChatRoomServer : IServer
{
    private BlockingCollection<Task> ScheduledTask { get; } = new();
    public IServiceProvider ServiceProvider => _container;

    public void Initialize()
    {
        _network = new(this);
        _container.RegisterSingleton<ILoggerManager, CmdServerLoggerManager>();
        _container.RegisterSingleton<IResourceManager, ResourceManager>();
        _container.RegisterSingleton<IUserService, UserService>();
        _container.RegisterSingleton<IChatRoomService, ChatRoomService>();
        _container.RegisterSingleton<IDatabase, Database.Database>();

        _container.RegisterInstance<INetwork, Network>(_network);
        _container.RegisterInstance<IServer, ChatRoomServer>(this);

        OnRegisterService?.Invoke(_container);

        _container.Freeze();

        NetworkService = _container.Resolve<INetwork>();
        LoggerManager = _container.Resolve<ILoggerManager>();
        LoggerManager.StartService();
        Database = _container.Resolve<IDatabase>();
        Database.Connect();
    }

    public void Start()
    {
        if (NetworkService is null) throw new NetworkServiceException();
        NetworkService.StartService();
        InitChannels();
        InitUserService();
        StartScheduler();
    }

    public void Stop()
    {
        if (NetworkService is null) throw new NetworkServiceException();
        SchedulerThread?.Interrupt();
        NetworkService.StopService();
    }

    public void AddScheduledTask(Action task)
    {
        ScheduledTask.Add(new(task));
    }

    private void StartScheduler()
    {
        SchedulerThread = new(() =>
        {
            foreach (var task in ScheduledTask.GetConsumingEnumerable())
                task.Start();
        });
        SchedulerThread.Start();
    }

    private void InitChannels()
    {
        InitUserChannel();
    }

    private void InitUserService()
    {
        if (NetworkService is null) throw new NetworkServiceException();
    }

    private void InitUserChannel()
    {
        User = NetworkService.New(Names.Channel.User);
        User.Register<AuthenticationReqMessage, AuthenticationMessageHandler>();
        User.Register<AuthenticationResultMsg>();
        User.Register<RegisterRequestMessage, RegisterRequestMessageHandler>();
        User.Register<RegisterResultMessage>();
        User.Register<JoinRoomRequestMessage, JoinRoomRequestMessageHandler>();
        User.Register<JoinRoomResultMsg>();
        User.Register<CreateRoomReqMsg, CreateRoomReqMessageHandler>();
        User.Register<CreateRoomResultMsg>();
        User.Register<JoinedRoomsInfoMsg>();

        Friend = NetworkService.New(Names.Channel.Friend);
        Friend.Register<AddFriendRequestMessage, AddFriendReqMessageHandler>();
        Friend.Register<AddFriendReplyMessage, AddFriendReplyMessageHandler>();
        Friend.Register<ReceivedFriendRequestsInfoMessage>();
        Friend.Register<SentFriendRequestsResultsMessage>();

        Chatting = NetworkService.New(Names.Channel.Chatting);
        Chatting.Register<ChatMessage, ChatMessageHandler>();
    }

    private Thread? SchedulerThread { get; set; }

#nullable disable
    private readonly ServiceContainer _container = new()
    {
        HotReload = false
    };

    private Network _network;

    public IDatabase Database { get; set; }

    public event OnRegisterServiceHandler OnRegisterService;

    public INetwork NetworkService
    {
        get => _network;
        private set => _network = (Network)value;
    }

    public IMessageChannel User { get; private set; }
    public IMessageChannel Chatting { get; private set; }
    public IMessageChannel Friend { get; private set; }

    public ILoggerManager LoggerManager { get; private set; }
#nullable enable
}

[Serializable]
public class NetworkServiceException : Exception
{
    public NetworkServiceException()
    {
    }

    public NetworkServiceException(string message) : base(message)
    {
    }

    public NetworkServiceException(string message, Exception inner) : base(message, inner)
    {
    }

    protected NetworkServiceException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}