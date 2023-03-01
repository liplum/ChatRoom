using ChatRoom.Core.Models;
using ChatRoom.Core.Network;
using Newtonsoft.Json.Linq;

namespace ChatRoom.Core.Message;

[Msg("AddFriendReq", Direction.ClientToServer)]
public class AddFriendRequestMessage : IMessage
{
#nullable disable
    public string FromAccount { get; set; }
    public string ToAccount { get; set; }
#nullable enable
    public int VerificationCode { get; set; }

    public void Serialize(dynamic json)
    {
        json.From = FromAccount;
        json.To = ToAccount;
        json.VCode = VerificationCode;
    }

    public void Deserialize(dynamic json)
    {
        FromAccount = json.From;
        ToAccount = json.To;
        VerificationCode = json.VCode;
    }
}

[Msg("AddFriendReply", Direction.ClientToServer)]
public class AddFriendReplyMessage : IMessage
{
#nullable disable
    public string Account { get; set; }
#nullable enable
    public int VerificationCode { get; set; }
    public FriendRequestResult Result { get; set; } = FriendRequestResult.None;

    public int RequestId { get; set; }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.VCode = VerificationCode;
        json.RequestID = RequestId;
        json.Result = (int)Result;
    }

    public void Deserialize(dynamic json)
    {
        Account = json.Account;
        VerificationCode = json.VCode;
        RequestId = json.RequestID;
        Result = (FriendRequestResult)json.Result;
    }
}

[Msg("ReceivedFriendRequestsInfo", Direction.ServerToClient)]
public class ReceivedFriendRequestsInfoMessage : IMessage
{
#nullable disable
    public string Account { get; set; }
    public object[] FriendRequests { get; set; }
#nullable enable

    public int VerificationCode { get; set; }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Requests = JArray.FromObject(FriendRequests);
        json.VCode = VerificationCode;
    }

    public void Deserialize(dynamic json)
    {
        throw new NotImplementedException();
    }
}

[Msg("SentFriendRequestsResults", Direction.ServerToClient)]
public class SentFriendRequestsResultsMessage : IMessage
{
#nullable disable
    public string Account { get; set; }
    public object[] Results { get; set; }
#nullable enable

    public int VerificationCode { get; set; }

    public void Serialize(dynamic json)
    {
        json.Account = Account;
        json.Requests = JArray.FromObject(Results);
        json.VCode = VerificationCode;
    }

    public void Deserialize(dynamic json)
    {
        throw new NotImplementedException();
    }
}