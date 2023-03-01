using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core;
using ChatRoom.Core.Models;
using ChatRoom.Core.Network;
using ChatRoom.Core.User;

namespace ChatRoom.Server.Interfaces;
public interface IUserService : IInjectable {
    public void RegisterUser(string account, string clearPassword, DateTime registerTime);

    public bool Verify(string account, string clearPassword);

    public bool VerifyAndOnline(NetworkToken clientToken, DateTime loginTime, string account, string clearPassword, [MaybeNullWhen(false)] out IUserEntity entity);

    public IUserEntity? FindOnline(string account);

    public IUserEntity? FindOnline(NetworkToken token);

    public bool TryGetByAccount(string account,[NotNullWhen(true)] out User? user);

    public bool DeleteUser(string account);

    public bool RecoverUser(string account);

    public bool NameNotOccupied(string account);

    public bool IsOnline(string account);

    public bool Online(string account, DateTime loginTime, NetworkToken clientToken);

    public bool Offline(string account);

    public bool Offline(NetworkToken token);
}