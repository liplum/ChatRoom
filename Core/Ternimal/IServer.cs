using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users;
using System.Diagnostics.CodeAnalysis;
using Room = ChattingRoom.Core.ChattingRoom;
namespace ChattingRoom.Core;
public interface IServer
{
    public void Initialize();

    public void Start();

    public Room? GetChattingRoomBy(ChattingRoomID ID);

    public UserID GenAvailableUserID();

    public void RegisterUser(UserID userID);

    public IMessageChannel? GetMessageChannelBy(string name);

    public bool Verify(UserID id, string password);

    public event OnRegisterServiceHandler OnRegisterService;

    public void AddScheduledTask([NotNull] Task<Action> action);

    public delegate void OnRegisterServiceHandler([NotNull] IServiceRegistry registry);
}

