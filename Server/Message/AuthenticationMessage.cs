using ChattingRoom.Core.Networks;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Server.Messages;
public class AuthenticationMessage : IMessage
{
    public int? ClientID{get;private set;}
    public ChattingRoom(){}

    public ChattingRoom(int clientID){
	ClientID=clientID;
    }
    
    public void Deserialize(dynamic json)
    {
	ClientID=json.ClientID;
    }

    public void Serialize(dynamic json)
    {
	if(ClientID is not null){
		json.ClientID=ClientID;
	}
    }
}

public class AuthenticationMessageHandler : IMessageHandler<AuthenticationMessage>
{
    public void Handle([NotNull] AuthenticationMessage msg, dynamic context)
    {
	IServer server = context;
	int? ClientID=msg.ClientID;
	if(ClientID is not null){
		
	}
    }
}
