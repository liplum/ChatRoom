using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Models;
using ChatRoom.Core.Network;
using ChatRoom.Core.User;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Services;
public class ChatRoomService : IChatRoomService {
    public bool TryGetById(int chatRoomId, [NotNullWhen(true)] out Room? chatRoom) {
        chatRoom = (from cr in Db.ChatRoomTable where cr.ChatRoomId == chatRoomId && cr.IsActive select cr).FirstOrDefault();
        return chatRoom is not null;
    }

    public MemberType GetRelationship(Room room, User user, out Membership? membership) {
        if (room.IsActive) {
            Db.Context.Entry(room)
                .Collection(r => r.Members)
                .Load();
            membership = (from m in room.Members where m.User == user select m).FirstOrDefault();
            return membership?.Type ?? MemberType.None;
        }
        membership = null;
        return MemberType.None;
    }

    public void ReceiveNewText(Room room, IUserEntity sender, string text, DateTime sendTimeClient) {
        if (!room.IsActive) return;
        Db.Context.Entry(room).Collection(r => r.Members).Load();
        Logger.SendTip("[Chatting]Received a text.");
        foreach (var member in from m in room.Members where m.IsActive && m.Type is not MemberType.None select m.User) {
            var ue = Users.FindOnline(member.Account);
            if (ue is null || !ue.IsOnline || !ue.Info.IsActive) continue;
            Chatting.SendMessage(ue.Token,
                new ChatMessage {
                    Account = sender.Account,
                    SendTime = DateTime.UtcNow,
                    Text = text,
                    ChatRoomId = room.ChatRoomId,
                    VerificationCode = ue.VerificationCode
                });
            Logger.SendTip($"[Chatting]A Text was sent to {ue.Account}.");
        }
    }

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime, [NotNullWhen(true)] out int? chatRoomId) {
        roomName ??= user.NickName;
        var room = new Room {
            Name = roomName,
            IsActive = true,
            CreatedTime = createdTime,
            MemberCount = 1
        };
        Db.ChatRoomTable.Add(room);

        var membership = new Membership {
            IsActive = true,
            User = user,
            Room = room,
            Type = MemberType.Owner,
            CreatedTime = createdTime
        };
        room.Members.Add(membership);
        user.Joined.Add(membership);
        user.CreatedRoomCount++;
        Db.SaveChange();
        chatRoomId = room.ChatRoomId;
        Logger.SendTip($"Chat room {chatRoomId}-{roomName} was created by {user.Account}.");
        return true;
    }

    public bool JoinChatRoom(User user, Room room, DateTime joinTime, Membership? membership = null) {
        if (membership is not null) {
            membership.IsActive = true;
            membership.Type = MemberType.Member;
            membership.CreatedTime = joinTime;
        }
        else {
            membership = new() {
                IsActive = true,
                User = user,
                Room = room,
                Type = MemberType.Member,
                CreatedTime = joinTime
            };
            room.Members.Add(membership);
            user.Joined.Add(membership);
        }
        room.MemberCount++;
        user.JoinedRoomCount++;
        Db.SaveChange();
        Logger.SendTip($"User {user.Account} joined the chat room {room.ChatRoomId}-{room.Name}.");
        return true;
    }

    public bool IsExisted(int chatRoomId, [NotNullWhen(true)] out Room? chatRoom) {
        return TryGetById(chatRoomId, out chatRoom);
    }

    public IEnumerable<Room> AllJoinedRoom(User user) {
        Membership Load(Membership membership) {
            Db.Context.Entry(membership).Reference(m => m.Room).Load();
            return membership;
        }
        if (!user.IsActive) return Array.Empty<Room>();
        Db.Context.Entry(user).Collection(r => r.Joined).Load();
        return (from m in user.Joined
                where m.IsActive && m.Type is not MemberType.None
                let room = Load(m).Room
                where m.IsActive
                select room).ToArray();
    }

    public bool IsJoined(User user, Room room, [NotNullWhen(true)] out Membership? membership) {
        if (!user.IsActive) {
            membership = null;
            return false;
        }
        return GetRelationship(room, user, out membership) is not MemberType.None;
    }

    public void Initialize(IServiceProvider serviceProvider) {
        Db = serviceProvider.Resolve<IDatabase>();
        Network = serviceProvider.Resolve<INetwork>();
        Logger = serviceProvider.Resolve<ILogger>();
        Users = serviceProvider.Resolve<IUserService>();
        User = Network.GetMessageChannelBy("User");
        Chatting = Network.GetMessageChannelBy("Chatting");
    }
#nullable disable
    private IDatabase Db {
        get;
        set;
    }
    private INetwork Network {
        get;
        set;
    }
    private IUserService Users {
        get;
        set;
    }
    private IMessageChannel User {
        get;
        set;
    }
    private IMessageChannel Chatting {
        get;
        set;
    }
    private ILogger Logger {
        get;
        set;
    }
#nullable enable
}