using ChatRoom.Core.Interface;
using IServiceProvider = ChatRoom.Core.Interface.IServiceProvider;

namespace ChatRoom.Core.Ternimal;
public interface IServer {

    public delegate void OnRegisterServiceHandler(IServiceRegistry registry);

    public IServiceProvider ServiceProvider {
        get;
    }
    public void Initialize();

    public void Start();

    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask(Action task);
}