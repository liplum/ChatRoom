using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;
public class AuthenticationMsgHandler : IMessageHandler<AuthenticationReqMsg> {
    public void Handle([NotNull] AuthenticationReqMsg msg, MessageContext context) {
        var loginTime = DateTime.UtcNow;
        var target = context.ClientToken;
        if (target is null) return;

        var server = context.Server;
        var account = msg.Account;
        var password = msg.Password;
        var sp = server.ServiceProvider;
        var userService = sp.Resolve<IUserService>();
        var channel = context.Channel;
        AuthenticationResultMsg reply;
        if (userService.VerifyAndOnline(target, loginTime, account, password, out var entity)) {
            var vcode = entity.VerificationCode;
            reply = new() {
                Ok = true,
                Account = account,
                VerificationCode = vcode
            };
            var logger = sp.Resolve<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication succeed.");
            channel.SendMessage(target, reply);

            var chatRoom = sp.Resolve<IChatRoomService>();
            Shared.SendAllJoinedRoomList(channel, chatRoom, entity);
            var friend = context.Network.GetMessageChannelBy(Names.Channel.Friend)!;
            Shared.SendUnhandledRequests(sp, friend, entity);
        }
        else {
            reply = new() {
                Ok = false,
                Account = account
            };
            var logger = sp.Resolve<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication failed.");
            channel.SendMessage(target, reply);
        }
    }

}