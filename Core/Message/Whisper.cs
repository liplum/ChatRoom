using ChattingRoom.Core.Networks;

namespace ChattingRoom.Core.Messages;
[Msg("Whisper", Direction.ClientToServer, Direction.ServerToClient)]
public class WhisperMsg : IMessage
{

    public WhisperMsg()
    {

    }

    public UserID? Target { get; set; }
    public UserID? Sender { get; set; }

    public string? Text { get; set; }

    public void Deserialize(dynamic json)
    {

    }

    public void Serialize(dynamic json)
    {
    }
}
