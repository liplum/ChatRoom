namespace ChattingRoom.Core.Messages;

[Msg("RegisterRequest", Direction.ClientToServer)]
public class RegisterRequestMsg : IMessage
{
#nullable disable
    public string Account
    {
        get; set;
    }
#nullable enable
    public string? Password
    {
        get; set;
    }
    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        Password = json.Password;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        if (Password is not null)
        {
            json.Password = Password;
        }
    }
}

[Msg("RegisterResult", Direction.ServerToClient)]
public class RegisterResultMsg : IMessage
{
    public enum Result
    {
        Failed = -1,
        NoFinalResult = 0,
        Succeed = 1,
    }

    public enum FailureCause
    {
        AccountOccupied = 0,
        InvalidAccount = 1,
        InvalidPassword = 2,
        Forbidden = 3,
    }

#nullable disable
    public string Account
    {
        get; set;
    }

    public Result Res
    {
        get; set;
    }
#nullable enable

    public FailureCause? Cause
    {
        get; set;
    }

    public RegisterResultMsg()
    {

    }

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        Res = (Result)json.Result;
        if (Res == Result.Failed)
        {
            Cause = (FailureCause)json.Cause;
        }
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Result = (int)Res;
        if (Cause.HasValue)
        {
            json.Cause = (int)Cause.Value;
        }
    }
}