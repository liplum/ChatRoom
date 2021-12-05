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
        var userService = server.ServiceProvider.Resolve<IUserService>();
        AuthenticationResultMsg reply;
        if (userService.VerifyAndOnline(target, loginTime, account, password, out var entity)) {
            var vcode = entity.VerificationCode;
            reply = new() {
                Ok = true,
                Account = account,
                VerificationCode = vcode
            };
            var logger = server.ServiceProvider.Resolve<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication succeed.");
            context.Channel.SendMessage(target, reply);

            var chatRoom = server.ServiceProvider.Resolve<IChatRoomService>();
            var joined = (from r in chatRoom.AllJoinedRoom(entity.Info) select new { ChatRoomID = r.ChatRoomId, r.Name }).ToArray();
            context.Channel.SendMessage(target, new JoinedRoomsInfoMsg {
                Account = account,
                VerificationCode = vcode,
                AllJoined = joined
            });
        }
        else {
            reply = new() {
                Ok = false,
                Account = account
            };
            var logger = server.ServiceProvider.Resolve<ILogger>();
            logger.SendTip($"[User][Authentication]User \"{account}\" authentication failed.");
            context.Channel.SendMessage(target, reply);
        }
    }
}