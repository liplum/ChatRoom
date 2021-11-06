using ChattingRoom.Core.Networks;

namespace ChattingRoom.Server.Messages;
public class RegisterRequestMsgHandler : IMessageHandler<RegisterRequestMsg>
{
    public void Handle([NotNull] RegisterRequestMsg msg, MessageContext context)
    {
        var token = context.ClientToken;
        if (token is not null)
        {
            var server = context.Server;
            var userService = server.UserService!;
            var id = userService.GenAvailableUserID();
            try
            {
                userService.RegisterUser(id);
                context.Channel.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Succeed));
            }
            catch (Exception)
            {
                context.Channel.SendMessage(token, new RegisterResultMsg(RegisterResultMsg.RegisterResult.Failed, RegisterResultMsg.FailureCause.Forbidden));
            }
        }

    }
}