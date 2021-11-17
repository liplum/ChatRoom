global using ChattingRoom.Core.Networks;
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

    public int VerificationCode
    {
        get; set;
    }

#nullable enable
    public void Deserialize(dynamic json)
    {
        ChattingText = json.Text;
        Account = json.Account;
        long timestamp = json.TimeStamp;
        SendTime = timestamp.ToUnixDatetime();
        ChattingRoomID = json.ChattingRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Text = ChattingText;
        json.ChattingRoomID = ChattingRoomID;
        json.TimeStamp = new DateTimeOffset(SendTime).ToUnixTimeSeconds();
        json.VCode = VerificationCode;
    }
}