using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users;
using ChattingRoom.Core.Utils;

namespace ChattingRoom.Core.Messages;

[Msg("Authentication", Direction.ClientToServer)]
public class AuthenticationMsg : IMessage
{
    public UserID? ID { get; set; }
    public string? Password { get; set; }
    public AuthenticationMsg() { }

    public void Deserialize(dynamic json)
    {
        ID = new(json.ClientID);
        Password = json.Password;
    }

    public void Serialize(dynamic json)
    {
        json.ClientID = ID!.Value.Name;
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

    public AuthResult? Result { get; set; }

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
        var res = Result!.Value;
        json.Result = (int)res;
    }
}