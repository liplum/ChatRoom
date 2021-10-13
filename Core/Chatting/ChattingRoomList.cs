namespace ChattingRoom.Core;
public class ChattingRoomList
{
    private readonly Dictionary<int, ChattingRoom> _allChatingRooms = new();
    public ChattingRoom? this[int ID]
    {
        get => _allChatingRooms.TryGetValue(ID, out var chatingRoom) ? chatingRoom : null;
    }
}
