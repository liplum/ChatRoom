using ChattingRoom.Core.DB.Models;
using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Services;
public class ChattingRoomService : IChattingRoomService
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
    private readonly Dictionary<int, ChatRoom> _cache = new();
    public ChatRoom? ByID(int chattingRoomID)
    {
        if (_cache.TryGetValue(chattingRoomID, out var room))
        {
            if (room.IsActive)
            {
                return room;
            }
            else
            {
                _cache.Remove(chattingRoomID);
                return null;
            }
        }
        var target = (from cr in DB.ChattingRoomTable where cr.ChattingRoomID == chattingRoomID select cr).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            _cache[chattingRoomID] = target;
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
        User = Network.GetMessageChannelBy("User");
        Chatting = Network.GetMessageChannelBy("Chatting");
    }

    public void ReceviceNewText(ChatRoom room, IUserEntity sender, string chattingText, DateTime SendTimeClient)
    {
        Logger.SendTip("Recevied a text.");
        Chatting.SendMessage(Network.AllConnectedClient,
            new ChattingMsg()
            {
                Account = sender.Account,
                SendTime = DateTime.UtcNow,
                ChattingText = chattingText,
                ChattingRoomID = room.ChattingRoomID
            });
    }
}