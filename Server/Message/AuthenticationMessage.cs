using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Messages;
public class AuthenticationMessage : IMessage
{
    public void Deserialize(dynamic json)
    {

    }

    public void Serialize(dynamic json)
    {

    }
}

public class AuthenticationMessageHandler : IMessageHandler<AuthenticationMessage>
{
    public void Handle([NotNull] AuthenticationMessage msg, dynamic context)
    {

    }
}
