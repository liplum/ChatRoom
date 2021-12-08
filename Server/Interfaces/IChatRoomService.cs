namespace ChattingRoom.Server.Interfaces;
public interface IChatRoomService : IInjectable {
    public bool TryGetById(int chatRoomId, [NotNullWhen(true)] out ChatRoom? chatRoom);

    public void ReceiveNewText(ChatRoom room, IUserEntity sender, string text, DateTime sendTimeClient);

    public MemberType GetRelationship(ChatRoom room, User user, out Membership? membership);

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime, [NotNullWhen(true)] out int? chatRoomId);

    public bool IsExisted(int chatRoomId, [NotNullWhen(true)] out ChatRoom? chatRoom);

    public bool JoinChatRoom(User user, ChatRoom room, DateTime joinTime, Membership? membership = null);

    public ChatRoom[] AllJoinedRoom(User user);

    public bool IsJoined(User user, ChatRoom room, [NotNullWhen(true)] out Membership? membership);
}