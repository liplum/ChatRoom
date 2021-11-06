using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.Core.Messages;

[Msg("Chatting", Direction.ClientToServer, Direction.ServerToClient)]
public class ChattingMsg : IMessage
{
    public ChattingMsg()
    {

    }

    public UserID? UserID { get; set; }
    public string? ChattingText { get; set; }

    public DateTime? SendTime { get; set; }

    public ChattingRoomID? ChattingRoomID { get; set; }

    public void Deserialize(dynamic json)
    {
        string? user_id_string = json.UserID;
        ChattingText = json.Text;
        long? sendtime_long = json.TimeStamp;
        int? roomID = json.ChattingRoomID;
        if (!(user_id_string, ChattingText, sendtime_long, roomID).NotNull())
        {
            throw new Exception($"A parameter is null.");
        }
        UserID = new(user_id_string);
        SendTime = sendtime_long.Value.ToUnixDatetime();
        ChattingRoomID = new(roomID.Value);
    }

    public void Serialize(dynamic json)
    {
        if (!(UserID, ChattingText, SendTime, ChattingRoomID).NotNull())
        {
            throw new Exception($"A parameter is null.");
        }
        json.UserID = UserID!.Value.Name;
        json.Text = ChattingText;
        json.ChattingRoomID = ChattingRoomID!.Value.ID;
        json.TimeStamp = new DateTimeOffset(SendTime!.Value).ToUnixTimeSeconds();
    }
}

public class ChattingMsgHandler : IMessageHandler<ChattingMsg>
{
    public void Handle([NotNull] ChattingMsg msg, MessageContext context)
    {
        var server = context.Server;
        var room = server.GetChattingRoomBy(msg.ChattingRoomID!.Value);
        room?.AddChattingItem(msg.UserID!.Value, msg.ChattingText!, msg.SendTime!.Value);
    }
}