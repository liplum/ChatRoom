using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Models;
using ChatRoom.Core.Network;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Message;

public class AddFriendReqMessageHandler : IMessageHandler<AddFriendRequestMessage>
{
    public void Handle(AddFriendRequestMessage message, MessageContext context)
    {
        var server = context.Server;
        var now = DateTime.UtcNow;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = message.VerificationCode;
        var from = userService.FindOnline(message.FromAccount);
        if (from is null || !from.Info.IsActive || from.VerificationCode != vcode) return;
        if (userService.TryGetByAccount(message.ToAccount, out var to))
        {
            var fqService = server.ServiceProvider.Resolve<IFriendService>();
            if (!fqService.HasFriendRequest(from.Info, to, out _))
            {
                fqService.AddFriendRequest(from.Info, to, now, out _);
            }
        }
    }
}

public class AddFriendReplyMessageHandler : IMessageHandler<AddFriendReplyMessage>
{
    public void Handle(AddFriendReplyMessage message, MessageContext context)
    {
        if (message.Result is FriendRequestResult.None) return;
        var server = context.Server;
        var now = DateTime.UtcNow;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = message.VerificationCode;
        var user = userService.FindOnline(message.Account);
        if (user is null || !user.Info.IsActive || user.VerificationCode != vcode) return;
        var u = user.Info;
        var fqService = server.ServiceProvider.Resolve<IFriendService>();
        if (!fqService.TryGetById(message.RequestId, out var fq) || fq.To != u) return;
        switch (message.Result)
        {
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