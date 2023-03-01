using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core;
using ChatRoom.Core.Models;
using ChatRoom.Core.User;

namespace ChatRoom.Server.Interfaces;

public interface IChatRoomService : IInjectable
{
    public bool TryGetById(int chatRoomId, [NotNullWhen(true)] out Room? chatRoom);

    public void ReceiveNewText(Room room, IUserEntity sender, string text, DateTime sendTimeClient);

    public MemberType GetRelationship(Room room, User user, out Membership? membership);

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime,
        [NotNullWhen(true)] out int? chatRoomId);

    public bool IsExisted(int chatRoomId, [NotNullWhen(true)] out Room? chatRoom);

    public bool JoinChatRoom(User user, Room room, DateTime joinTime, Membership? membership = null);

    public IEnumerable<Room> AllJoinedRoom(User user);

    public bool IsJoined(User user, Room room, [NotNullWhen(true)] out Membership? membership);
}