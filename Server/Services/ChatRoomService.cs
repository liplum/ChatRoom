using System.Collections.Concurrent;
using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Services;
public class ChatRoomService : IChatRoomService
{
#nullable disable
    private IDatabase DB
    {
        get; set;
    }
    private INetwork Network
    {
        get; set;
    }
    private IUserService Users
    {
        get; set;
    }
    private IMessageChannel User
    {
        get; set;
    }
    private IMessageChannel Chatting
    {
        get; set;
    }
    private ILogger Logger
    {
        get; set;
    }
#nullable enable
    private readonly ConcurrentDictionary<int, ChatRoom> _cache = new();
    public ChatRoom? ByID(int chatRoomID)
    {
        if (_cache.TryGetValue(chatRoomID, out var room))
        {
            if (room.IsActive)
            {
                return room;
            }
            else
            {
                _cache.TryRemove(chatRoomID, out _);
                return null;
            }
        }
        var target = (from cr in DB.ChatRoomTable where cr.ChatRoomID == chatRoomID select cr).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            _cache[chatRoomID] = target;
            return target;
        }
        return null;
    }

    public MemberType GetRelationship(ChatRoom room, User user)
    {
        if (room.IsActive)
        {
            DB.Context.Entry(room)
                .Collection(r => r.Members)
                .Load();
            var relationship = (from m in room.Members where m.User == user select m.Type).FirstOrDefault();
            return relationship;
        }
        return MemberType.None;
    }

    public void Initialize(IServiceProvider serviceProvider)
    {
        DB = serviceProvider.Reslove<IDatabase>();
        Network = serviceProvider.Reslove<INetwork>();
        Logger = serviceProvider.Reslove<ILogger>();
        Users = serviceProvider.Reslove<IUserService>();
        User = Network.GetMessageChannelBy("User");
        Chatting = Network.GetMessageChannelBy("Chatting");
    }

    public void ReceviceNewText(ChatRoom room, IUserEntity sender, string text, DateTime SendTimeClient)
    {
        if (room.IsActive)
        {
            DB.Context.Entry(room).Collection(r => r.Members).Load();
            Logger.SendTip("[Chatting]Recevied a text.");
            foreach (var member in from m in room.Members where m.IsActive && m.Type is not MemberType.None select m.User)
            {
                var uentity = Users.FindOnline(member.Account);
                if (uentity is not null && uentity.IsOnline && uentity.Info.IsActive)
                {
                    Chatting.SendMessage(uentity.Token,
                        new ChattingMsg()
                        {
                            Account = sender.Account,
                            SendTime = DateTime.UtcNow,
                            Text = text,
                            ChatRoomID = room.ChatRoomID,
                            VerificationCode = uentity.VerificationCode
                        });
                    Logger.SendTip($"[Chatting]A Text was sent to {uentity.Account}.");
                }
            }
        }
    }

    public bool CreateNewChatRoom(User user, string? roomName, DateTime createdTime, [NotNullWhen(true)] out int? chatRoomID)
    {
        roomName ??= user.NickName;
        var room = new ChatRoom()
        {
            Name = roomName,
            IsActive = true,
            CreatedTime = createdTime,
            MemberCount = 1
        };
        var membership = new Membership()
        {
            IsActive = true,
            User = user,
            ChatRoom = room,
            Type = MemberType.Owner,
            CreatedTime = createdTime
        };
        room.Members.Add(membership);
        user.Joined.Add(membership);
        user.CreatedRoomCount++;
        DB.ChatRoomTable.Add(room);
        DB.MembershipTable.Add(membership);
        DB.SaveChange();
        chatRoomID = room.ChatRoomID;
        Logger.SendTip($"Chat room {chatRoomID}-{roomName} was created by {user.Account}.");
        return true;
    }

    public bool JoinChatRoom(User user, ChatRoom room, DateTime joinTime)
    {
        var membership = new Membership()
        {
            IsActive = true,
            User = user,
            ChatRoom = room,
            Type = MemberType.Member,
            CreatedTime = joinTime
        };
        room.Members.Add(membership);
        room.MemberCount++;
        user.Joined.Add(membership);
        user.JoinedRoomCount++;
        DB.MembershipTable.Add(membership);
        DB.SaveChange();
        Logger.SendTip($"User {user.Account} joined the chat room {room.ChatRoomID}-{room.Name}.");
        return true;
    }

    public bool IsExisted(int chatRoomID, [NotNullWhen(true)] out ChatRoom? chatRoom)
    {
        chatRoom = ByID(chatRoomID);
        return chatRoom is not null;
    }

    public ChatRoom[] AllJoinedRoom(User user)
    {
        Membership Load(Membership membership)
        {
            DB.Context.Entry(membership).Reference(m => m.ChatRoom).Load();
            return membership;
        }
        if (!user.IsActive)
        {
            return Array.Empty<ChatRoom>();
        }
        DB.Context.Entry(user).Collection(r => r.Joined).Load();
        return (from m in user.Joined
                where m.IsActive && m.Type is not MemberType.None
                let room = Load(m).ChatRoom
                where m.IsActive
                select room).ToArray();
    }

    public bool IsJoined(User user, ChatRoom room)
    {
        if (!user.IsActive)
        {
            return false;
        }
        return GetRelationship(room, user) is not MemberType.None;
    }
}