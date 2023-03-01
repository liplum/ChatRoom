using ChattingRoom.Core.Networks;
using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Messages;
public class JoinRoomRequestMsgHandler : IMessageHandler<JoinRoomRequestMsg> {
    public void Handle([NotNull] JoinRoomRequestMsg msg, MessageContext context) {
        var target = context.ClientToken;
        if (target is null) return;
        var server = context.Server;
        var account = msg.Account;
        var vcode = msg.VerificationCode;
        var user = server.ServiceProvider.Resolve<IUserService>();
        var uentity = user.FindOnline(account);
        if (uentity is null || !uentity.Info.IsActive || uentity.VerificationCode != vcode) return;
        var u = uentity.Info;
        var roomid = msg.ChatRoomId;
        JoinRoomResultMsg reply = new() {
            Account = account,
            ChatRoomId = roomid,
            VerificationCode = vcode
        };
        var channel = context.Channel;
        var chatroom = server.ServiceProvider.Resolve<IChatRoomService>();
        if (chatroom.IsExisted(roomid, out var room)) {
            if (chatroom.IsJoined(u, room, out var membership)) {
                reply.Res = JoinRoomResultMsg.Result.AlreadyJoined;
                channel.SendMessage(target, reply);
            }
            else {
                var joinTime = DateTime.UtcNow;
                if (chatroom.JoinChatRoom(u, room, joinTime, membership)) {
                    reply.Res = JoinRoomResultMsg.Result.Succeed;
                    channel.SendMessage(target, reply);
                    Shared.SendAllJoinedRoomList(channel, chatroom, uentity);
                }
                else {
                    reply.Res = JoinRoomResultMsg.Result.Forbidden;
                    channel.SendMessage(target, reply);
                }
            }
        }
        else {
            reply.Res = JoinRoomResultMsg.Result.NotFound;
            channel.SendMessage(target, reply);
        }

    }
}

public class CreateRoomReqMsgHandler : IMessageHandler<CreateRoomReqMsg> {
    public void Handle([NotNull] CreateRoomReqMsg msg, MessageContext context) {
        var target = context.ClientToken;
        if (target is null) return;
        var server = context.Server;
        var account = msg.Account;
        var vcode = msg.VerificationCode;
        var user = server.ServiceProvider.Resolve<IUserService>();
        var uentity = user.FindOnline(account);
        if (uentity is null || !uentity.Info.IsActive || uentity.VerificationCode != vcode) return;
        var u = uentity.Info;
        CreateRoomResultMsg reply = new() {
            Account = account,
            VerificationCode = vcode
        };
        var channel = context.Channel;
        var createdTime = DateTime.UtcNow;
        var roomName = msg.ChatRoomName;
        var chatroom = server.ServiceProvider.Resolve<IChatRoomService>();
        if (chatroom.CreateNewChatRoom(u, roomName, createdTime, out var id)) {

            reply.ChatRoomId = id.Value;
            reply.Res = CreateRoomResultMsg.Result.Succeed;
            channel.SendMessage(target, reply);
            Shared.SendAllJoinedRoomList(channel, chatroom, uentity);
        }
        else {
            reply.Res = CreateRoomResultMsg.Result.Forbidden;
            channel.SendMessage(target, reply);
        }
    }
}

public class ChatRoomInfoReqMsgHandler : IMessageHandler<ChatRoomInfoReqMsg> {
    public void Handle([NotNull] ChatRoomInfoReqMsg msg, MessageContext context) {
        var target = context.ClientToken;
        if (target is null) return;
        var server = context.Server;
        var account = msg.Account;
        var vcode = msg.VerificationCode;
        var user = server.ServiceProvider.Resolve<IUserService>();
        var uentity = user.FindOnline(account);
        if (uentity is null || !uentity.Info.IsActive || uentity.VerificationCode != vcode) return;
        var ctrService = server.ServiceProvider.Resolve<IChatRoomService>();
        var roomid = msg.ChatRoomId;
        if (ctrService.TryGetById(roomid, out var room)) {
            var u = uentity.Info;
            var r = ctrService.GetRelationship(room, u, out var membership);
            if (r == MemberType.None) return;
            var members = (
                from m in room.Members
                where m.IsActive
                let usr = m.User
                where usr.IsActive
                select new {
                    usr.Account,
                    usr.NickName
                }).ToArray();
            ChatRoomInfoReplyMsg reply = new() {
                Account = account,
                VerificationCode = vcode,
                ChatRoomId = roomid,
                Info = members
            };
        }
    }
}