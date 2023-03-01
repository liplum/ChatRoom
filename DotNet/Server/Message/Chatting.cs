using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Network;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Message;
public class ChattingMsgHandler : IMessageHandler<ChattingMsg> {
    public void Handle([NotNull] ChattingMsg msg, MessageContext context) {
        var server = context.Server;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = msg.VerificationCode;
        var user = userService.FindOnline(msg.Account);
        if (user is null || !user.Info.IsActive || user.VerificationCode != vcode) return;
        var ctrService = server.ServiceProvider.Resolve<IChatRoomService>();
        if (ctrService.TryGetById(msg.ChatRoomId, out var room)) {
            ctrService.ReceiveNewText(room, user, msg.Text, msg.SendTime);
        }
    }
}