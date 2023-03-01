using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core;
using ChatRoom.Core.Models;
using ChatRoom.Core.User;

namespace ChatRoom.Server.Interfaces;
public interface IChatRoomService : IInjectable {
    public bool TryGetById(int chatRoomId, [NotNullWhen(true)] out Core.Models.ChatRoom? chatRoom);

    public void ReceiveNewText(Core.Models.ChatRoom room, IUserEntity sender, string text, DateTime sendTimeClient);

    public MemberType GetRelationship(Core.Models.ChatRoom room, User user, out Membership? membership);

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime, [NotNullWhen(true)] out int? chatRoomId);

    public bool IsExisted(int chatRoomId, [NotNullWhen(true)] out Core.Models.ChatRoom? chatRoom);

    public bool JoinChatRoom(User user, Core.Models.ChatRoom room, DateTime joinTime, Membership? membership = null);

    public Core.Models.ChatRoom[] AllJoinedRoom(User user);

    public bool IsJoined(User user, Core.Models.ChatRoom room, [NotNullWhen(true)] out Membership? membership);
}