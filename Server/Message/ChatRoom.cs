using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;
public class JoinRoomRequestMsgHandler : IMessageHandler<JoinRoomRequestMsg>
{
    public void Handle([NotNull] JoinRoomRequestMsg msg, MessageContext context)
    {
        var target = context.ClientToken;
        if (target is null)
        {
            return;
        }
        var server = context.Server;
        var account = msg.Account;
        var roomid = msg.ChatRoomID;
        var vcode = msg.VerificationCode;
        var user = server.ServiceProvider.Reslove<IUserService>();
        var uentity = user.FindOnline(account);
        if (uentity is null || uentity.VerificationCode != vcode)
        {
            return;
        }
        var u = uentity.Info;
        JoinRoomResultMsg reply = new()
        {
            Account = account,
            ChatRoomID = roomid,
            VerificationCode = vcode
        };
        var chatroom = server.ServiceProvider.Reslove<IChatRoomService>();
        if (chatroom.IsExisted(roomid, out var room))
        {
            if (chatroom.IsJoined(u, room))
            {
                reply.Res = JoinRoomResultMsg.Result.AlreadyJoined;
                context.Channel.SendMessage(target, reply);
            }
            else
            {
                var joinTime = DateTime.UtcNow;
                if (chatroom.JoinChatRoom(u, room, joinTime))
                {
                    reply.Res = JoinRoomResultMsg.Result.Succeed;
                    context.Channel.SendMessage(target, reply);
                    var joined = (from r in chatroom.AllJoinedRoom(u) select new { r.ChatRoomID, r.Name }).ToArray();
                    context.Channel.SendMessage(target, new JoinedRoomsInfoMsg()
                    {
                        Account = account,
                        VerificationCode = vcode,
                        AllJoined = joined
                    });
                }
                else
                {
                    reply.Res = JoinRoomResultMsg.Result.Forbidden;
                    context.Channel.SendMessage(target, reply);
                }
            }
        }
        else
        {
            reply.Res = JoinRoomResultMsg.Result.NotFound;
            context.Channel.SendMessage(target, reply);
        }

    }
}
public class CreateRoomReqMsgHandler : IMessageHandler<CreateRoomReqMsg>
{
    public void Handle([NotNull] CreateRoomReqMsg msg, MessageContext context)
    {
        var target = context.ClientToken;
        if (target is null)
        {
            return;
        }
        var server = context.Server;
        var account = msg.Account;
        var roomName = msg.ChatRoomName;
        var vcode = msg.VerificationCode;
        var user = server.ServiceProvider.Reslove<IUserService>();
        var uentity = user.FindOnline(account);
        if (uentity is null || uentity.VerificationCode != vcode)
        {
            return;
        }
        var u = uentity.Info;
        CreateRoomResultMsg reply = new()
        {
            Account = account,
            VerificationCode = vcode,
        };
        var createdTime = DateTime.UtcNow;
        var chatroom = server.ServiceProvider.Reslove<IChatRoomService>();
        if (chatroom.CreateNewChatRoom(u, roomName, createdTime, out var id))
        {

            reply.ChatRoomID = id.Value;
            reply.Res = CreateRoomResultMsg.Result.Succeed;
            context.Channel.SendMessage(target, reply);
            var joined = (from r in chatroom.AllJoinedRoom(u) select new { r.ChatRoomID, r.Name }).ToArray();
            context.Channel.SendMessage(target, new JoinedRoomsInfoMsg()
            {
                Account = account,
                VerificationCode = vcode,
                AllJoined = joined
            });
        }
        else
        {
            reply.Res = CreateRoomResultMsg.Result.Forbidden;
            context.Channel.SendMessage(target, reply);
        }
    }
}

public class ChatRoomInfoReqMsgHandler : IMessageHandler<ChatRoomInfoReqMsg>
{
    public void Handle([NotNull] ChatRoomInfoReqMsg msg, MessageContext context)
    {

    }
}
