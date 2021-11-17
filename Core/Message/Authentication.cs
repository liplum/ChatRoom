namespace ChattingRoom.Core.Messages;

[Msg("AuthenticationReq", Direction.ClientToServer)]
public class AuthenticationReqMsg : IMessage
{
#nullable disable
    public string Account
    {
        get; set;
    }
    public string Password
    {
        get; set;
    }
#nullable enable
    public AuthenticationReqMsg()
    {
    }

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        Password = json.Password;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Password = Password;
    }
}

[Msg("AuthenticationResult", Direction.ServerToClient)]
public class AuthenticationResultMsg : IMessage
{
    public AuthenticationResultMsg()
    {

    }
#nullable disable
    public string Account
    {
        get; set;
    }
#nullable enable
    public bool OK
    {
        get; set;
    }
    public int? VerificationCode
    {
        get; set;
    }

    public AuthenticationResultMsg(bool ok)
    {
        OK = ok;
    }

    public void Deserialize(dynamic json)
    {
        OK = json.OK;
        Account = json.Account;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.OK = OK;
        json.Account = Account;
        if (VerificationCode is not null)
        {
            json.VCode = VerificationCode;
        }
    }
}