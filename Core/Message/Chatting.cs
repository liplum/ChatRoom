global using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.Core.Messages;

[Msg("Chatting", Direction.ClientToServer, Direction.ServerToClient)]
public class ChattingMsg : IMessage
{
#nullable disable
    public string Account
    {
        get; set;
    }
    public string Text
    {
        get; set;
    }

    public DateTime SendTime
    {
        get; set;
    }

    public int ChatRoomID
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
        Text = json.Text;
        Account = json.Account;
        long timestamp = json.TimeStamp;
        SendTime = timestamp.ToUnixDatetime();
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Text = Text;
        json.ChatRoomID = ChatRoomID;
        json.TimeStamp = new DateTimeOffset(SendTime).ToUnixTimeSeconds();
        json.VCode = VerificationCode;
    }
}