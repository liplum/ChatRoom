namespace ChattingRoom.Core;
public interface IServer {

    public delegate void OnRegisterServiceHandler([NotNull] IServiceRegistry registry);

    public IServiceProvider ServiceProvider {
        get;
    }
    public void Initialize();

    public void Start();

    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask([NotNull] Action task);
}