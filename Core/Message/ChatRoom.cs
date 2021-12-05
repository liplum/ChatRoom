using Newtonsoft.Json.Linq;

namespace ChattingRoom.Core.Messages;
[Msg("JoinRoomReq", Direction.ClientToServer)]
public class JoinRoomRequestMsg : IMessage {

    public void Deserialize(dynamic json) {
        Account = json.Account;
        ChatRoomId = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.ChatRoomID = ChatRoomId;
        json.VCode = VerificationCode;
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int ChatRoomId {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }

#nullable enable
}

[Msg("JoinRoomResult", Direction.ServerToClient)]
public class JoinRoomResultMsg : IMessage {

    public enum Result {
        NotFound = -2,
        AlreadyJoined = -1,
        Forbidden = 0,
        Succeed = 1
    }

    public void Deserialize(dynamic json) {
        Account = json.Account;
        ChatRoomId = json.ChatRoomID;
        VerificationCode = json.VCode;
        Res = json.Result;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.ChatRoomID = ChatRoomId;
        json.VCode = VerificationCode;
        json.Result = (int)Res;
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int ChatRoomId {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }
    public Result Res {
        get;
        set;
    }

#nullable enable
}

[Msg("CreateRoomReq", Direction.ClientToServer)]
public class CreateRoomReqMsg : IMessage {
    public string? ChatRoomName {
        get;
        set;
    }

    public void Deserialize(dynamic json) {
        Account = json.Account;
        ChatRoomName = json.ChatRoomName;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.ChatRoomName = ChatRoomName;
        json.VCode = VerificationCode;
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }

#nullable enable
}

[Msg("CreateRoomResult", Direction.ServerToClient)]
public class CreateRoomResultMsg : IMessage {

    public enum Result {
        Maximum = -1,
        Forbidden = 0,
        Succeed = 1
    }

    public void Deserialize(dynamic json) {
        Account = json.Account;
        ChatRoomId = json.ChatRoomID;
        VerificationCode = json.VCode;
        Res = json.Result;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        if (ChatRoomId.HasValue) json.ChatRoomID = ChatRoomId;
        json.VCode = VerificationCode;
        json.Result = (int)Res;
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int? ChatRoomId {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }
    public Result Res {
        get;
        set;
    }

#nullable enable
}

[Msg("ChatRoomInfoReq", Direction.ClientToServer)]
public class ChatRoomInfoReqMsg : IMessage {

    public void Deserialize(dynamic json) {
        Account = json.Account;
        ChatRoomId = json.ChatRoomID;
        VerificationCode = json.VCode;
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.ChatRoomID = ChatRoomId;
        json.VCode = VerificationCode;
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int ChatRoomId {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }
#nullable enable
}

[Msg("ChatRoomInfoReply", Direction.ServerToClient)]
public class ChatRoomInfoReplyMsg : IMessage {

    public void Deserialize(dynamic json) {
        throw new NotImplementedException();
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.ChatRoomID = ChatRoomId;
        json.VCode = VerificationCode;
        json.Info = JArray.FromObject(Info);
    }

#nullable disable
    public string Account {
        get;
        set;
    }
    public int ChatRoomId {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }
    public object[] Info {
        get;
        set;
    }
#nullable enable
}

[Msg("JoinedRoomsInfo", Direction.ServerToClient)]
public class JoinedRoomsInfoMsg : IMessage {

    public void Deserialize(dynamic json) {
        throw new NotImplementedException();
    }

    public void Serialize(dynamic json) {
        json.Account = Account;
        json.AllJoined = JArray.FromObject(AllJoined);
        json.VCode = VerificationCode;
    }
#nullable disable
    public string Account {
        get;
        set;
    }
    public object[] AllJoined {
        get;
        set;
    }
    public int VerificationCode {
        get;
        set;
    }
#nullable enable
}