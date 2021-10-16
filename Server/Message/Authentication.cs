using ChattingRoom.Core.Messages;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users;
using ChattingRoom.Core.Utils;
using System.Diagnostics.CodeAnalysis;

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
            server.Verify(clientID!.Value, password!);
        }
    }
}
