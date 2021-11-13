using ChattingRoom.Core.DB.Models;

namespace ChattingRoom.Server.Interfaces;
public interface IChattingRoomService : IInjectable
{
    public ChatRoom? ByID(int chattingRoomID);

    public void ReceviceNewText(ChatRoom room, IUserEntity sender, string chattingText, DateTime SendTimeClient);

    public MemberType GetRelationship(ChatRoom room, User user);
}
