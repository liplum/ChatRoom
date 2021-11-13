using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;

public class AuthenticationMsgHandler : IMessageHandler<AuthenticationMsg>
{
    public void Handle([NotNull] AuthenticationMsg msg, MessageContext context)
    {
        var server = context.Server;
        var clientAccount = msg.Account;
        var password = msg.Password;
        var userService = server.ServiceProvider.Reslove<IUserService>();
        if ((clientAccount, password).NotNull())
        {
            userService.Verify(clientAccount, password, out var client);
        }
    }
}
