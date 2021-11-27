﻿using ChattingRoom.Core.Networks;

namespace ChattingRoom.Server.Interfaces;
public interface IUserService : IInjectable
{
    public void RegisterUser(string account, string clear_password, DateTime registerTime);

    public bool Verify(string account, string clear_password);

    public bool VerifyAndOnline(NetworkToken clientToken, DateTime loginTime, string account, string clear_password, [MaybeNullWhen(false)] out IUserEntity entity);

    public IUserEntity? FindOnline(string account);

    public IUserEntity? FindOnline(NetworkToken token);

    public bool DeleteUser(string account);

    public bool RecoverUser(string account);

    public bool NameNotOccupied(string account);

    public bool IsOnline(string account);

    public bool Online(string account, DateTime loginTime, NetworkToken clientToken);

    public bool Offline(string account);

    public bool Offline(NetworkToken token);
}
