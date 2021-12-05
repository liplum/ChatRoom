using ChattingRoom.Core.DB.Models;

namespace ChattingRoom.Core.Messages;
[Msg("AddFriendReq", Direction.ClientToServer, Direction.ServerToClient)]
public class AddFriendReqMsg : IMessage {

#nullable disable
    public string FromAccount {
        get;
        set;
    }
    public string ToAccount {
        get;
        set;
    }
#nullable enable
    public int VerificationCode {
        get;
        set;
    }
    public void Serialize(dynamic json) {

    }
    public void Deserialize(dynamic json) {

    }
}

[Msg("AddFriendReply", Direction.ClientToServer, Direction.ServerToClient)]
public class AddFriendReplyMsg : IMessage {

#nullable disable
    public string FromAccount {
        get;
        set;
    }
    public string ToAccount {
        get;
        set;
    }
#nullable enable
    public int VerificationCode {
        get;
        set;
    }
    public FriendRequestResult Result {
        get;
        set;
    } = FriendRequestResult.None;
    public void Serialize(dynamic json) {

    }
    public void Deserialize(dynamic json) {

    }
}

