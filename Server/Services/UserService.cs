using System.Collections.Concurrent;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users.Securities;

namespace ChattingRoom.Server.Interfaces;
public class UserService : IUserService {
    private ConcurrentDictionary<string, UserEntity> OnlineUsers {
        get;
    } = new();
    private ConcurrentDictionary<NetworkToken, UserEntity> OnlineUsersToken2Entity {
        get;
    } = new();

    public void RegisterUser(string account, string clearPassword, DateTime registerTime) {
        var encryptedPwd = clearPassword.Encrypted();
        Db.UserTable.Add(new() {
            Account = account,
            RegisterTime = registerTime,
            Password = encryptedPwd,
            IsActive = true,
            NickName = account
        });
        Db.SaveChange();
    }
    public bool DeleteUser(string account) {
        var target = (from u in Db.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is null || !target.IsActive) return false;
        target.IsActive = false;
        Db.SaveChange();
        return true;
    }

    public bool RecoverUser(string account) {
        var target = (from u in Db.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is null || target.IsActive) return false;
        target.IsActive = true;
        Db.SaveChange();
        return true;
    }

    public bool NameNotOccupied(string account) {
        var shouldBeNull = Db.UserTable.Find(account);
        return shouldBeNull is null;
    }

    public bool IsOnline(string account) {
        return true;
    }

    public bool Verify(string account, string clearPassword) {
        var target = (from u in Db.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive) return Md5.Verify(clearPassword, target.Password);
        return false;
    }

    public bool VerifyAndOnline(NetworkToken clientToken, DateTime loginTime, string account, string clearPassword, [MaybeNullWhen(false)] out IUserEntity entity) {
        UserEntity? res = null;

        var target = (from u in Db.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
            res = new() {
                Info = target,
                UserService = this,
                Token = clientToken,
                VerificationCode = Random.Shared.Next()
            };

        if (res is null) {
            entity = null;
            return false;
        }

        if (Md5.Verify(clearPassword, res.Info.Password)) {
            entity = res;
            OnlineUsers[account] = res;
            OnlineUsersToken2Entity[clientToken] = res;
            res.Info.LastLoginTime = loginTime;
            Db.SaveChange();
            return true;
        }
        entity = null;
        return false;
    }

    public IUserEntity? FindOnline(string account) {
        if (OnlineUsers.TryGetValue(account, out var user) && user.Info.IsActive) return user;
        return null;
    }

    public bool Online(string account, DateTime loginTime, NetworkToken clientToken) {
        if (OnlineUsers.ContainsKey(account)) return false;
        var target = (from u in Db.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive) {
            var entity = new UserEntity {
                Info = target,
                UserService = this,
                Token = clientToken,
                VerificationCode = Random.Shared.Next()
            };
            OnlineUsers[account] = entity;
            OnlineUsersToken2Entity[clientToken] = entity;
            target.LastLoginTime = loginTime;
            return true;
        }
        return false;
    }

    public bool Offline(string account) {
        if (OnlineUsers.TryGetValue(account, out var entity)) {
            OnlineUsersToken2Entity.TryRemove(entity.Token, out _);
            OnlineUsers.TryRemove(account, out _);
            return true;
        }
        return false;
    }
    public bool Offline(NetworkToken token) {
        if (OnlineUsersToken2Entity.TryGetValue(token, out var entity)) {
            OnlineUsers.TryRemove(entity.Account, out _);
            OnlineUsersToken2Entity.TryRemove(entity.Token, out _);
            return true;
        }
        return false;
    }

    public IUserEntity? FindOnline(NetworkToken token) {
        if (OnlineUsersToken2Entity.TryGetValue(token, out var user) && user.Info.IsActive) return user;
        return null;
    }

    public void Initialize(IServiceProvider serviceProvider) {
        Db = serviceProvider.Resolve<IDatabase>();
        Network = serviceProvider.Resolve<INetwork>();
        Network.OnClientDisconnected += (token => Offline(token))!;
    }

    private class UserEntity : IUserEntity {
        public bool IsOnline => UserService.OnlineUsersToken2Entity.ContainsKey(Token);

        public int VerificationCode {
            get;
            set;
        }

        public void SaveChange() {
            UserService.Db.SaveChange();
        }
#nullable disable
        public UserService UserService {
            get;
            set;
        }

        public User Info {
            get;
            set;

        }
        public NetworkToken Token {
            get;
            set;
        }
        public string Account => Info.Account;

#nullable enable
    }
#nullable disable
    private IDatabase Db {
        get;
        set;
    }
    private INetwork Network {
        get;
        set;
    }
#nullable enable
}