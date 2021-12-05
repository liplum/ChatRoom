using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;
public class ChattingMsgHandler : IMessageHandler<ChattingMsg> {
    public void Handle([NotNull] ChattingMsg msg, MessageContext context) {
        var server = context.Server;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var vcode = msg.VerificationCode;
        var user = userService.FindOnline(msg.Account);
        if (user is null || !user.Info.IsActive || user.VerificationCode != vcode) return;
        var ctrService = server.ServiceProvider.Resolve<IChatRoomService>();
        var room = ctrService.ById(msg.ChatRoomId);
        if (room is null) return;
        ctrService.ReceiveNewText(room, user, msg.Text, msg.SendTime);
    }
}