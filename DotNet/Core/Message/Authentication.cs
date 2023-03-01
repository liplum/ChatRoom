using ChatRoom.Core.Network;

namespace ChatRoom.Core.Message;
[Msg("AuthenticationReq", Direction.ClientToServer)]
public class AuthenticationReqMsg : IMessage {

    public void Deserialize(dynamic json) {
        Account = json.Account;
        Password = json.Password;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.Password = Password;
    }
#nullable disable
    public string Account {
        get;
        set;
    }
    public string Password {
        get;
        set;
    }
#nullable enable
}

[Msg("AuthenticationResult", Direction.ServerToClient)]
public class AuthenticationResultMsg : IMessage {
    public AuthenticationResultMsg() {

    }

    public AuthenticationResultMsg(bool ok) {
        Ok = ok;
    }
#nullable disable
    public string Account {
        get;
        set;
    }
#nullable enable
    public bool Ok {
        get;
        set;
    }
    public int? VerificationCode {
        get;
        set;
    }

    public void Deserialize(dynamic json) {
        Ok = json.OK;
        Account = json.Account;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json) {
        json.OK = Ok;
        json.Account = Account;
        if (VerificationCode is not null) json.VCode = VerificationCode;
    }
}