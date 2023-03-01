using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Network;
using ChatRoom.Core.User;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Message;
public static class Shared {
    public static void SendAllJoinedRoomList(IMessageChannel channel, IChatRoomService chatRoom, IUserEntity entity) {
        var joined = (
            from r in chatRoom.AllJoinedRoom(entity.Info)
            select new {
                ChatRoomID = r.ChatRoomId,
                r.Name
            }).ToArray();
        channel.SendMessage(entity.Token, new JoinedRoomsInfoMsg {
            Account = entity.Account,
            VerificationCode = entity.VerificationCode,
            AllJoined = joined
        });
    }
    public static void SendUnhandledRequests(IServiceProvider sp, IMessageChannel friend, IUserEntity entity) {
        var fs = sp.Resolve<IFriendService>();
        var token = entity.Token;
        var u = entity.Info;
        var account = u.Account;
        var vcode = entity.VerificationCode;
        var rfqs = fs.GetAllFriendRequestsTo(u);//Received
        if (rfqs.Length > 0) {
            var xrfqs = (
                from fq in rfqs
                select new {
                    RequestID = fq.FriendRequestId,
                    From = fq.From.Account,
                }).ToArray();
            friend.SendMessage(token, new ReceivedFriendRequestsInfoMessage {
                Account = account,
                VerificationCode = vcode,
                FriendRequests = xrfqs,
            });
        }
        var sfqs = fs.GetAllFriendRequestsFrom(u);//Sent
        if (sfqs.Length > 0) {
            var xsfqs = (
                from fq in sfqs
                select new {
                    RequestID = fq.FriendRequestId,
                    To = fq.To.Account,
                    Result = (int)fq.Result
                }).ToArray();
            friend.SendMessage(token,new SentFriendRequestsResultsMessage {
                Account = account,
                VerificationCode = vcode,
                Results = xsfqs
            });
        }
    }

}