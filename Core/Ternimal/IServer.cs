using ChattingRoom.Core.User;
using System.Diagnostics.CodeAnalysis;
using Room = ChattingRoom.Core.ChattingRoom;
namespace ChattingRoom.Core;
public interface IServer
{
    public void Initialize();

    public void Start();

    public Room? GetChattingRoomBy(ChattingRoomID ID);


    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask([NotNull] Action task);

    public delegate void OnRegisterServiceHandler([NotNull] IServiceRegistry registry);

    public IUserService? UserService { get; }
}

