using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Networks;
using System.Diagnostics.CodeAnalysis;
using Cause = ChattingRoom.Server.Messages.RegisterResultMsg.FailureCause;
using Result = ChattingRoom.Server.Messages.RegisterResultMsg.RegisterResult;

namespace ChattingRoom.Server.Messages;

public class RegisterRequestMsg : IMessage
{
    public void Deserialize(dynamic json)
    {

    }

    public void Serialize(dynamic json)
    {

    }
}

public class RegisterRequestMsgHandler : IMessageHandler<RegisterRequestMsg>
{
    public void Handle([NotNull] RegisterRequestMsg msg, MessageContext context)
    {
        var token = context.ClientToken;
        if (token is not null)
        {
            var server = context.Server;
            var id = server.GenAvailableUserID();
            try
            {
                server.RegisterUser(id);
                context.Channel.SendMessage(token, new RegisterResultMsg(Result.Succeed));
            }
            catch (Exception)
            {
                context.Channel.SendMessage(token, new RegisterResultMsg(Result.Failed, Cause.Forbidden));
            }
        }

    }
}

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

    private RegisterResult? Result { get; set; }
    private FailureCause? Cause { get; set; }

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