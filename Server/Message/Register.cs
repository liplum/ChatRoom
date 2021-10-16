using ChattingRoom.Core.Messages;
using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Messages;
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
                context.Channel.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
            }
            catch (Exception)
            {
                context.Channel.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Failed, RegisterResultMsg.FailureCause.Forbidden));
            }
        }

    }
}