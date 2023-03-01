using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Network;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Message;
public class AuthenticationMessageHandler : IMessageHandler<AuthenticationReqMessage> {
    public void Handle(AuthenticationReqMessage message, MessageContext context) {
        var loginTime = DateTime.UtcNow;
        var target = context.ClientToken;
        if (target is null) return;

        var server = context.Server;
        var account = message.Account;
        var password = message.Password;
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