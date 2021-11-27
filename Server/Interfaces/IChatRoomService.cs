namespace ChattingRoom.Server.Interfaces;
public interface IChatRoomService : IInjectable
{
    public ChatRoom? ByID(int chatRoomID);

    public void ReceviceNewText(ChatRoom room, IUserEntity sender, string text, DateTime cendTimeClient);

    public MemberType GetRelationship(ChatRoom room, User user);

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime, [NotNullWhen(true)] out int? chatRoomID);

    public bool IsExisted(int chatRoomID, [NotNullWhen(true)] out ChatRoom? chatRoom);

    public bool JoinChatRoom(User user, ChatRoom room, DateTime joinTime);

    public ChatRoom[] AllJoinedRoom(User user);

    public bool IsJoined(User user, ChatRoom room);
}
