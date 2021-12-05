namespace ChattingRoom.Core.Messages;
[Msg("UserInfo", Direction.ClientToServer, Direction.ServerToClient)]
public class UserInfoMsg : IMessage {

    public void Deserialize(dynamic json) {
        Account = json.Account;
        NickName = json.NickName;
        JoinedChattingRooms = json.AllJoined;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        if (NickName is not null) json.NickName = NickName;
        json.AllJoined = JoinedChattingRooms;
    }
#nullable disable
    public string Account {
        get;
        set;
    }
    public string NickName {
        get;
        set;
    }

    public object[] JoinedChattingRooms {
        get;
        set;
    }
#nullable enable
}

[Msg("ChangePassword", Direction.ClientToServer)]
public class ChangePasswordMsg : IMessage {
    public void Deserialize(dynamic json) {

    }

    public void Serialize(dynamic json) {

    }
}

[Msg("ChangePasswordResult", Direction.ServerToClient)]
public class ChangePasswordResultMsg : IMessage {
    public bool Ok {
        get;
        set;
    }

    public void Deserialize(dynamic json) {
        Ok = json.OK;
    }

    public void Serialize(dynamic json) {
        json.OK = Ok;
    }
}