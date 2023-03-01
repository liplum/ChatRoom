using ChatRoom.Core.Network;
using ChatRoom.Core.Util;

namespace ChatRoom.Core.Message;
[Msg("Whisper", Direction.ClientToServer, Direction.ServerToClient)]
public class WhisperMsg : IMessage {
#nullable disable
    public string Sender {
        get;
        set;
    }
    public string Receiver {
        get;
        set;
    }
    public string Text {
        get;
        set;
    }
#nullable enable
    public int VerificationCode {
        get;
        set;
    }
    public DateTime SendTime {
        get;
        set;
    }
    public void Deserialize(dynamic json) {
        Text = json.Text;
        Sender = json.Sender;
        Receiver = json.Receiver;
        long timestamp = json.TimeStamp;
        SendTime = timestamp.ToUnixDatetime();
        VerificationCode = json.VCode;
    }
    public void Serialize(dynamic json) {
        json.Sender = Sender;
        json.Receiver = Receiver;
        json.Text = Text;
        json.TimeStamp = new DateTimeOffset(SendTime).ToUnixTimeSeconds();
        json.VCode = VerificationCode;
    }
}

[Msg("WhisperResult", Direction.ClientToServer, Direction.ServerToClient)]
public class WhisperResultMsg : IMessage {
#nullable disable
    public string Sender {
        get;
        set;
    }
    public string Target {
        get;
        set;
    }
#nullable enable
    public void Deserialize(dynamic json) {
        
    }
    public void Serialize(dynamic json) {
    }
}