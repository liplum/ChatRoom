using ChattingRoom.Core;
using ChattingRoom.Server.Networks;
using Room = ChattingRoom.Core.ChattingRoom;
namespace ChattingRoom.Server;
public interface IServer
{
    public void Initialize();

    public void Start();

    public Room? GetChattingRoomBy(ChattingRoomID ID);

    public UserID GenAvailableUserID();

    public void RegisterUser(UserID userID);

    public IMessageChannel? GetMessageChannelBy(string name);
}
