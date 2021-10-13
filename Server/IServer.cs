namespace ChattingRoom.Server;
public interface IServer
{
    public void Initialize();

    public void Start();

    public ChattingRoom? GetChattingRoomBy(ChattingRoomID ID);

    public bool RegisterUser(int UserID);
}
