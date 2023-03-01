using ChatRoom.Core.Network;
using ChatRoom.Core.Util;

namespace ChatRoom.Core.Message;

[Msg("Chatting", Direction.ClientToServer, Direction.ServerToClient)]
public class ChatMessage : IMessage
{
#nullable disable
    public string Account { get; set; }
    public string Text { get; set; }
#nullable enable
    public DateTime SendTime { get; set; }

    public int ChatRoomId { get; set; }

    public int VerificationCode { get; set; }

    public void Deserialize(dynamic json)
    {
        Text = json.Text;
        Account = json.Account;
        long timestamp = json.TimeStamp;
        SendTime = timestamp.ToUnixDatetime();
        ChatRoomId = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Text = Text;
        json.ChatRoomID = ChatRoomId;
        json.TimeStamp = new DateTimeOffset(SendTime).ToUnixTimeSeconds();
        json.VCode = VerificationCode;
    }
}