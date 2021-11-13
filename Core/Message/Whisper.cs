using ChattingRoom.Core.Networks;

namespace ChattingRoom.Core.Messages;
[Msg("Whisper", Direction.ClientToServer, Direction.ServerToClient)]
public class WhisperMsg : IMessage
{

    public WhisperMsg()
    {

    }
#nullable disable
    public string Target
    {
        get; set;
    }
    public string Sender
    {
        get; set;
    }

    public string Text
    {
        get; set;
    }
#nullable enable

    public void Deserialize(dynamic json)
    {

    }

    public void Serialize(dynamic json)
    {
    }
}
