﻿using ChatRoom.Core.Interface;
using ChatRoom.Core.Message;
using ChatRoom.Core.Network;
using ChatRoom.Core.User;
using ChatRoom.Server.Interfaces;
using static ChatRoom.Core.Message.RegisterResultMessage;

namespace ChatRoom.Server.MessageHandler;

public class RegisterRequestMessageHandler : IMessageHandler<RegisterRequestMessage>
{
    public void Handle(RegisterRequestMessage message, MessageContext context)
    {
        var token = context.ClientToken;
        if (token is null) return;
        var server = context.Server;
        var userService = server.ServiceProvider.Resolve<IUserService>();
        var logger = server.ServiceProvider.Resolve<ILoggerManager>();
        var account = message.Account;
        var password = message.Password;
        RegisterResultMessage reply = new()
        {
            Account = account
        };

        if (!Account.IsValid(account))
        {
            reply.Res = Result.Failed;
            reply.Cause = FailureCause.InvalidAccount;
        }
        else //Account is valid
        {
            var isOccupied = !userService.NameNotOccupied(account);
            if (isOccupied)
            {
                reply.Res = Result.Failed;
                reply.Cause = FailureCause.AccountOccupied;
            }
            else //Account is not occupied
            {
                if (password is null)
                {
                    reply.Res = Result.NoFinalResult;
                }
                else
                {
                    if (Password.IsValid(password))
                    {
                        userService.RegisterUser(account, password, DateTime.UtcNow);
                        reply.Res = Result.Succeed;
                    }
                    else
                    {
                        reply.Res = Result.Failed;
                        reply.Cause = FailureCause.InvalidPassword;
                    }
                }
            }
        }

        switch (reply.Res)
        {
            case Result.Failed:
                logger.SendTip($"[User][Register]User \"{account}\"'s register failed.");
                break;
            case Result.Succeed:
                logger.SendTip($"[User][Register]User \"{account}\" successfully registered.");
                break;
        }

        context.Channel.SendMessage(token, reply);
    }
}