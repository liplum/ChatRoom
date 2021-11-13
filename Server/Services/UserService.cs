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
    private readonly Dictionary<string, UserEntity> _cache = new();

    public void RegisterUser(string account, string clear_password, DateTime registerTime)
    {
        var encryptedPwd = MD5.Convert(clear_password);
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

    public bool Verify(string account, string clear_password, out IUserEntity? entity)
    {
        UserEntity? res = null;
        if (_cache.TryGetValue(account, out var user))
        {
            res = user.Info.IsActive ? user : null;
        }
        else
        {
            var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
            if (target is not null && target.IsActive)
            {
                res = new UserEntity()
                {
                    Info = target,
                    UserService = this,
                };
                _cache[account] = res;
            }
        }

        if (res is null)
        {
            entity = null;
            return false;
        }

        if (MD5.Verify(clear_password, res.Info.Password))
        {
            entity = res;
            return true;
        }
        else
        {
            entity = null;
            return false;
        }
    }

    public IUserEntity? ByAccount(string account)
    {
        if (_cache.TryGetValue(account, out var user))
        {
            if (user.Info.IsActive)
            {
                return user;
            }
            else
            {
                _cache.Remove(account);
                return null;
            }
        }
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            var newEntity = new UserEntity()
            {
                Info = target,
                UserService = this,
            };
            _cache[account] = newEntity;
            return newEntity;
        }
        return null;
    }

    public bool DeleteUser(string account)
    {
        _cache.Remove(account);
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
    }

    public bool NotOccupied(string account)
    {
        var shouldBeNull = DB.UserTable.Find(account);
        return shouldBeNull is null;
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
        public bool IsOnline => Token is not null && UserService.Network.IsConnected(Token);
#nullable enable
        public NetworkToken? Token
        {
            get; set;
        }
        public void SaveChange()
        {
            UserService.DB.SaveChange();
        }
    }
}
