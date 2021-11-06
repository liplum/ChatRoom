using ChattingRoom.Core.Networks;

namespace ChattingRoom.Server.Messages;

public class AuthenticationMsgHandler : IMessageHandler<AuthenticationMsg>
{
    public void Handle([NotNull] AuthenticationMsg msg, MessageContext context)
    {
        var server = context.Server;
        UserID? clientID = msg.ID;
        string? password = msg.Password;
        if ((clientID, password).NotNull())
        {
            server?.UserService?.Verify(clientID!.Value, password!);
        }
    }
}
