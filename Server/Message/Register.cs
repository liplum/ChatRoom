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
        var logger = server.ServiceProvider.Reslove<ILogger>();
        var account = msg.Account;
        var password = msg.Password;
        RegisterResultMsg reply = new()
        {
            Account = account
        };

        if (!Account.IsValid(account))
        {
            reply.Res = Result.Failed;
            reply.Cause = FailureCause.InvalidAccount;
        }
        else//Account is valid
        {
            var isOccupied = !userService.NameNotOccupied(account);
            if (isOccupied)
            {
                reply.Res = Result.Failed;
                reply.Cause = FailureCause.AccountOccupied;
            }
            else//Account is not occupied
            {
                if (password is null)
                {
                    reply.Res = Result.NoFinalResult;
                }
                else
                {
                    if (Password.IsValid(password))
                    {
                        userService.RegisterUser(account, password, DateTime.UtcNow);
                        reply.Res = Result.Succeed;
                    }
                    else
                    {
                        reply.Res = Result.Failed;
                        reply.Cause = FailureCause.InvalidPassword;
                    }
                }
            }
        }
        switch (reply.Res)
        {
            case Result.Failed:
                logger.SendTip($"[User][Register]User \"{account}\"'s register failed.");
                break;
            case Result.Succeed:
                logger.SendTip($"[User][Register]User \"{account}\" successfully registered.");
                break;
        }
        context.Channel.SendMessage(token, reply);
    }
}