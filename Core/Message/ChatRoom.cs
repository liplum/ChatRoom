using Newtonsoft.Json.Linq;

namespace ChattingRoom.Core.Messages;

[Msg("JoinRoomReq", Direction.ClientToServer)]
public class JoinRoomRequestMsg : IMessage
{

#nullable disable
    public string Account
    {
        get; set;
    }
    public int ChatRoomID
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }

#nullable enable

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.ChatRoomID = ChatRoomID;
        json.VCode = VerificationCode;
    }
}


[Msg("JoinRoomResult", Direction.ServerToClient)]
public class JoinRoomResultMsg : IMessage
{

    public enum Result
    {
        NotFound = -2,
        AlreadyJoined = -1,
        Forbidden = 0,
        Succeed = 1,
    }

#nullable disable
    public string Account
    {
        get; set;
    }
    public int ChatRoomID
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }
    public Result Res
    {
        get; set;
    }

#nullable enable

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
        Res = json.Result;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.ChatRoomID = ChatRoomID;
        json.VCode = VerificationCode;
        json.Result = (int)Res;
    }
}


[Msg("CreateRoomReq", Direction.ClientToServer)]
public class CreateRoomReqMsg : IMessage
{

#nullable disable
    public string Account
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }

#nullable enable
    public string? ChatRoomName
    {
        get; set;
    }

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomName = json.ChatRoomName;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.ChatRoomName = ChatRoomName;
        json.VCode = VerificationCode;
    }
}


[Msg("CreateRoomResult", Direction.ServerToClient)]
public class CreateRoomResultMsg : IMessage
{

    public enum Result
    {
        Maximum = -1,
        Forbidden = 0,
        Succeed = 1,
    }

#nullable disable
    public string Account
    {
        get; set;
    }
    public int? ChatRoomID
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }
    public Result Res
    {
        get; set;
    }

#nullable enable

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
        Res = json.Result;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        if (ChatRoomID.HasValue)
        {
            json.ChatRoomID = ChatRoomID;
        }
        json.VCode = VerificationCode;
        json.Result = (int)Res;
    }
}


[Msg("ChatRoomInfoReq", Direction.ClientToServer)]
public class ChatRoomInfoReqMsg : IMessage
{

#nullable disable
    public string Account
    {
        get; set;
    }
    public int ChatRoomID
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }
#nullable enable

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.ChatRoomID = ChatRoomID;
        json.VCode = VerificationCode;
    }
}


[Msg("ChatRoomInfoReply", Direction.ServerToClient)]
public class ChatRoomInfoReplyMsg : IMessage
{

#nullable disable
    public string Account
    {
        get; set;
    }
    public int ChatRoomID
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }
    public object[] Info
    {
        get; set;
    }
#nullable enable

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        ChatRoomID = json.ChatRoomID;
        VerificationCode = json.VCode;
        Info = json.Info;
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.ChatRoomID = ChatRoomID;
        json.VCode = VerificationCode;
        json.Info = Info;
    }
}

[Msg("JoinedRoomsInfo", Direction.ServerToClient)]
public class JoinedRoomsInfoMsg : IMessage
{
#nullable disable
    public string Account
    {
        get; set;
    }
    public object[] AllJoined
    {
        get; set;
    }
    public int VerificationCode
    {
        get; set;
    }
#nullable enable

    public void Deserialize(dynamic json)
    {
        throw new NotImplementedException();
    }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.AllJoined = JArray.FromObject(AllJoined);
        json.VCode = VerificationCode;
    }
}