using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users.Securities;
using ChattingRoom.Server.Interfaces;
using static ChattingRoom.Core.Messages.RegisterResultMsg;

namespace ChattingRoom.Server.Messages;
public class RegisterRequestMsgHandler : IMessageHandler<RegisterRequestMsg>
{
    public void Handle([NotNull] RegisterRequestMsg msg, MessageContext context)
    {
        var token = context.ClientToken;
        if (token is null)
        {
            return;
        }
        var server = context.Server;
        var userService = server.ServiceProvider.Reslove<IUserService>();
        var account = msg.Account;
        var password = msg.Password;
        RegisterResultMsg reply;

        if (!Account.IsValid(account))
        {
            reply = new(RegisterResult.Failed, FailureCause.InvaildAccount);
        }
        else//Account is valid
        {
            var isOccupied = !userService.NameNotOccupied(account);
            if (isOccupied)
            {
                reply = new(RegisterResult.Failed, FailureCause.AccountOccupied);
            }
            else//Account is not occupied
            {
                if (password is null)
                {
                    reply = new(RegisterResult.NoFinalResult);
                }
                else
                {
                    if (Password.IsValid(password))
                    {
                        userService.RegisterUser(account, password, DateTime.UtcNow);
                        reply = new(RegisterResult.Succeed);
                    }
                    else
                    {
                        reply = new(RegisterResult.Failed, FailureCause.InvaildPassword);
                    }
                }
            }
        }
        context.Channel.SendMessage(token, reply);
    }
}