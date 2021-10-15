using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users;
using ChattingRoom.Core.Utils;
using ChattingRoom.Server.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Messages;

[Direction(Direction.ClientToServer)]
public class AuthenticationMsg : IMessage
{
    public UserID? ID { get; set; }
    public string? Password { get; set; }
    public AuthenticationMsg() { }

    public void Deserialize(dynamic json)
    {
        ID = new(json.ClientID);
        Password = json.Password;
    }

    public void Serialize(dynamic json)
    {
        json.ClientID = ID!.Value.Name;
        json.Password = Password;
    }
}

public class AuthenticationMsgHandler : IMessageHandler<AuthenticationMsg>
{
    public void Handle([NotNull] AuthenticationMsg msg, MessageContext context)
    {
        var server = context.Server;
        UserID? clientID = msg.ID;
        string? password = msg.Password;
        if (clientID is not null && password is not null)
        {
            if ((clientID, password).NotNull())
            {

            }
        }
    }
}
