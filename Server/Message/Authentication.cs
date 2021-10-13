using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Messages;
public class AuthenticationMsg : IMessage
{
    public int? UserID { get; private set; }
    public AuthenticationMsg() { }

    public AuthenticationMsg(int userClientID)
    {
        UserID = userClientID;
    }

    public void Deserialize(dynamic json)
    {
        UserID = json.ClientID;
    }

    public void Serialize(dynamic json)
    {
        if (UserID is not null)
        {
            json.ClientID = UserID;
        }
    }
}

public class AuthenticationMsgHandler : IMessageHandler<AuthenticationMsg>
{
    public void Handle([NotNull] AuthenticationMsg msg, MessageContext context)
    {
        var server = context.Server;
        int? ClientID = msg.UserID;
        if (ClientID is not null)
        {

        }
    }
}
