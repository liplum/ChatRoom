using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;
using ILogger = ChattingRoom.Core.ILogger;

namespace ChattingRoom.Server.Messages;

public class AuthenticationMsgHandler : IMessageHandler<AuthenticationReqMsg>
{
    public void Handle([NotNull] AuthenticationReqMsg msg, MessageContext context)
    {
        var target = context.ClientToken;
        if (target is null)
        {
            return;
        }
        var server = context.Server;
        var account = msg.Account;
        var password = msg.Password;
        var userService = server.ServiceProvider.Reslove<IUserService>();
        AuthenticationResultMsg reply;
        if (userService.VerifyAndOnline(target, account, password, out var entity))
        {
            var vcode = entity.VerificationCode;
            reply = new()
            {
                OK = true,
                Account = account,
                VerificationCode = vcode
            };
            var logger = server.ServiceProvider.Reslove<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication succeed.");
        }
        else
        {
            reply = new()
            {
                OK = false,
                Account = account,
            };
            var logger = server.ServiceProvider.Reslove<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication failed.");
        }
        context.Channel.SendMessage(target, reply);
    }
}