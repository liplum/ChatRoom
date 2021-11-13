namespace ChattingRoom.Core;
public interface IServer
{
    public void Initialize();

    public void Start();

    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask([NotNull] Action task);

    public IServiceProvider ServiceProvider
    {
        get;
    }

    public delegate void OnRegisterServiceHandler([NotNull] IServiceRegistry registry);
}

