using System.Collections.Concurrent;
using ChattingRoom.Core.Networks;
using ChattingRoom.Core.Users.Securities;

namespace ChattingRoom.Server.Interfaces;
public class UserService : IUserService
{
#nullable disable
    private IDatabase DB
    {
        get; set;
    }
    private INetwork Network
    {
        get; set;
    }
#nullable enable
    private ConcurrentDictionary<string, UserEntity> OnlineUsers { get; init; } = new();
    private ConcurrentDictionary<NetworkToken, UserEntity> OnlineUsers_Token2Entity { get; init; } = new();

    public void RegisterUser(string account, string clear_password, DateTime registerTime)
    {
        var encryptedPwd = clear_password.Encrypted();
        DB.UserTable.Add(new()
        {
            Account = account,
            RegisterTime = registerTime,
            Password = encryptedPwd,
            IsActive = true,
            NickName = account,
        });
        DB.SaveChange();
    }
    public bool DeleteUser(string account)
    {
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is null || !target.IsActive)
        {
            return false;
        }
        target.IsActive = false;
        DB.SaveChange();
        return true;
    }

    public bool RecoverUser(string account)
    {
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is null || target.IsActive)
        {
            return false;
        }
        target.IsActive = true;
        DB.SaveChange();
        return true;
    }

    public void Initialize(IServiceProvider serviceProvider)
    {
        DB = serviceProvider.Reslove<IDatabase>();
        Network = serviceProvider.Reslove<INetwork>();
        Network.OnClientDisconnected += (token => Offline(token))!;
    }

    public bool NameNotOccupied(string account)
    {
        var shouldBeNull = DB.UserTable.Find(account);
        return shouldBeNull is null;
    }

    public bool IsOnline(string account)
    {
        return true;
    }

    public bool Verify(string account, string clear_password)
    {
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            return MD5.Verify(clear_password, target.Password);
        }
        return false;
    }

    public bool VerifyAndOnline(NetworkToken clientToken, DateTime loginTime, string account, string clear_password, [MaybeNullWhen(false)] out IUserEntity entity)
    {
        UserEntity? res = null;

        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            res = new UserEntity()
            {
                Info = target,
                UserService = this,
                Token = clientToken,
                VerificationCode = Random.Shared.Next()
            };
        }

        if (res is null)
        {
            entity = null;
            return false;
        }

        if (MD5.Verify(clear_password, res.Info.Password))
        {
            entity = res;
            OnlineUsers[account] = res;
            OnlineUsers_Token2Entity[clientToken] = res;
            res.Info.LastLoginTime = loginTime;
            DB.SaveChange();
            return true;
        }
        else
        {
            entity = null;
            return false;
        }
    }

    public IUserEntity? FindOnline(string account)
    {
        if (OnlineUsers.TryGetValue(account, out var user) && user.Info.IsActive)
        {
            return user;
        }
        return null;
    }

    public bool Online(string account, DateTime loginTime, NetworkToken clientToken)
    {
        if (OnlineUsers.ContainsKey(account))
        {
            return false;
        }
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            var entity = new UserEntity()
            {
                Info = target,
                UserService = this,
                Token = clientToken,
                VerificationCode = Random.Shared.Next()
            };
            OnlineUsers[account] = entity;
            OnlineUsers_Token2Entity[clientToken] = entity;
            target.LastLoginTime = loginTime;
            return true;
        }
        return false;
    }

    public bool Offline(string account)
    {
        if (OnlineUsers.TryGetValue(account, out var entity))
        {
            OnlineUsers_Token2Entity.TryRemove(entity.Token, out _);
            OnlineUsers.TryRemove(account, out _);
            return true;
        }
        return false;
    }
    public bool Offline(NetworkToken token)
    {
        if (OnlineUsers_Token2Entity.TryGetValue(token, out var entity))
        {
            OnlineUsers.TryRemove(entity.Account, out _);
            OnlineUsers_Token2Entity.TryRemove(entity.Token, out _);
            return true;
        }
        return false;
    }

    public IUserEntity? FindOnline(NetworkToken token)
    {
        if (OnlineUsers_Token2Entity.TryGetValue(token, out var user) && user.Info.IsActive)
        {
            return user;
        }
        return null;
    }

    private class UserEntity : IUserEntity
    {
#nullable disable
        public UserService UserService
        {
            get; set;
        }

        public User Info
        {
            get; set;

        }
        public NetworkToken Token
        {
            get; set;
        }
        public string Account => Info.Account;

#nullable enable
        public bool IsOnline => UserService.OnlineUsers_Token2Entity.ContainsKey(Token);

        public int VerificationCode
        {
            get; set;
        }

        public void SaveChange()
        {
            UserService.DB.SaveChange();
        }
    }
}
