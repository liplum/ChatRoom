namespace ChattingRoom.Core.Messages;

[Msg("JoinRoomRequest", Direction.ClientToServer)]
public class JoinRoomRequestMessage : IMessage
{

#nullable disable
    public string Account
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

    }

    public void Serialize(dynamic json)
    {

    }
}
