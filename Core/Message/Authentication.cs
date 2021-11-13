using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.Core.Messages;

[Msg("Authentication", Direction.ClientToServer)]
public class AuthenticationMsg : IMessage
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
    public AuthenticationMsg()
    {
    }

    public void Deserialize(dynamic json)
    {
        Account = new(json.ClientID);
        Password = json.Password;
    }

    public void Serialize(dynamic json)
    {
        json.ClientID = Account;
        json.Password = Password;
    }
}

[Msg("AuthenticationResult", Direction.ServerToClient)]
public class AuthenticationResultMsg : IMessage
{
    public enum AuthResult
    {
        Succeed = 0,
        Failed = 1,
    }

    public AuthenticationResultMsg()
    {

    }
#nullable disable
    public AuthResult Result
    {
        get; set;
    }
#nullable enable

    public AuthenticationResultMsg(AuthResult result)
    {
        Result = result;
    }

    public void Deserialize(dynamic json)
    {
        int? result = json.Result;
        if (result.NotNull())
        {
            Result = (AuthResult)result.Value;
        }
    }

    public void Serialize(dynamic json)
    {
        var res = Result;
        json.Result = (int)res;
    }
}