using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Models;
using ChatRoom.Core.Network;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Message;
public class AddFriendReqMessageHandler : IMessageHandler<AddFriendReqMsg> {
    public void Handle([NotNull] AddFriendReqMsg msg, MessageContext context) {
        var server = context.Server;
        var now = DateTime.UtcNow;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = msg.VerificationCode;
        var from = userService.FindOnline(msg.FromAccount);
        if (from is null || !from.Info.IsActive || from.VerificationCode != vcode) return;
        if (userService.TryGetByAccount(msg.ToAccount, out var to)) {
            var fqService = server.ServiceProvider.Resolve<IFriendService>();
            if (!fqService.HasFriendRequest(from.Info, to, out _)) {
                fqService.AddFriendRequest(from.Info, to, now, out _);
            }
        }
    }
}

public class AddFriendReplyMsgHandler : IMessageHandler<AddFriendReplyMsg> {
    public void Handle([NotNull] AddFriendReplyMsg msg, MessageContext context) {
        if (msg.Result is FriendRequestResult.None) return;
        var server = context.Server;
        var now = DateTime.UtcNow;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = msg.VerificationCode;
        var user = userService.FindOnline(msg.Account);
        if (user is null || !user.Info.IsActive || user.VerificationCode != vcode) return;
        var u = user.Info;
        var fqService = server.ServiceProvider.Resolve<IFriendService>();
        if (fqService.TryGetById(msg.RequestId, out var fq) && fq.To == u) {
            switch (msg.Result) {
                case FriendRequestResult.Accept:
                case FriendRequestResult.Dismiss:
                    fqService.RemoveFriendRequest(fq);
                    break;
                case FriendRequestResult.Refuse:
                    fq.Result = FriendRequestResult.Refuse;
                    break;
            }
        }
    }
}