namespace ChattingRoom.Server;
public class ChatingRoomList
{
    private readonly Dictionary<int, ChatingRoom> _allChatingRooms = new();
    public ChatingRoom? this[int ID]
    {
        get => _allChatingRooms.TryGetValue(ID, out var chatingRoom) ? chatingRoom : null;
    }
}
