using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.Core.Messages;

[Msg("Chatting", Direction.ClientToServer, Direction.ServerToClient)]
public class ChattingMsg : IMessage
{
    public ChattingMsg()
    {

    }

#nullable disable
    public string Account
    {
        get; set;
    }
    public string ChattingText
    {
        get; set;
    }

    public DateTime SendTime
    {
        get; set;
    }

    public int ChattingRoomID
    {
        get; set;
    }

#nullable enable
    public void Deserialize(dynamic json)
    {
        string? user_id_string = json.Account;
        ChattingText = json.Text;
        long? sendtime_long = json.TimeStamp;
        int? roomID = json.ChattingRoomID;
        if (!(user_id_string, ChattingText, sendtime_long, roomID).NotNull())
        {
            throw new Exception($"A parameter is null.");
        }
        Account = new(user_id_string);
        SendTime = sendtime_long.Value.ToUnixDatetime();
        ChattingRoomID = roomID.Value;
    }

    public void Serialize(dynamic json)
    {
        if (!(Account, ChattingText, SendTime, ChattingRoomID).NotNull())
        {
            throw new Exception($"A parameter is null.");
        }
        json.Account = Account;
        json.Text = ChattingText;
        json.ChattingRoomID = ChattingRoomID;
        json.TimeStamp = new DateTimeOffset(SendTime).ToUnixTimeSeconds();
    }
}