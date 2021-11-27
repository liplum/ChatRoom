using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;
public class ChattingMsgHandler : IMessageHandler<ChattingMsg>
{
    public void Handle([NotNull] ChattingMsg msg, MessageContext context)
    {
        var server = context.Server;
        var ctrService = server.ServiceProvider.Reslove<IChatRoomService>();
        var room = ctrService.ByID(msg.ChatRoomID);
        if (room is null)
        {
            return;
        }
        var userService = server.ServiceProvider.Reslove<IUserService>();
        var user = userService.FindOnline(msg.Account);
        if (user is null)
        {
            return;
        }
        ctrService.ReceviceNewText(room, user, msg.Text, msg.SendTime);
    }
}
