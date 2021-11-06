using ChattingRoom.Core.Networks;

namespace ChattingRoom.Core.Messages;

[Msg("RegisterRequest", Direction.ClientToServer)]
public class RegisterRequestMsg : IMessage
{
    public void Deserialize(dynamic json)
    {

    }

    public void Serialize(dynamic json)
    {

    }
}

[Msg("RegisterResult", Direction.ServerToClient)]
public class RegisterResultMsg : IMessage
{
    public enum RegisterResult
    {
        Succeed = 0,
        Failed = 1,
    }

    public enum FailureCause
    {
        AlreadyRegistered = 0,
        ReachedMaxUserNumber = 1,
        Forbidden = 2,
    }

    public RegisterResultMsg()
    {

    }

    public RegisterResult? Result { get; set; }
    public FailureCause? Cause { get; set; }

    public RegisterResultMsg(RegisterResult result, [AllowNull] FailureCause? failureCause = null)
    {
        Result = result;
        Cause = failureCause;
    }

    public void Deserialize(dynamic json)
    {
        int? result = json.Result;
        int? cause = json.Cause;
        if (result.HasValue)
        {
            Result = (RegisterResult)result.Value;
            if (Result == RegisterResult.Failed && cause.HasValue)
            {
                Cause = (FailureCause)cause;
            }
        }
    }

    public void Serialize(dynamic json)
    {
        var res = Result!.Value;
        json.Result = (int)res;
        if (Cause.HasValue)
        {
            json.Cause = (int)Cause.Value;
        }
    }
}