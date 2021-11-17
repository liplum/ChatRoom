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
    private Dictionary<string, UserEntity> OnlineUsers { get; init; } = new();

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
        throw new NotImplementedException();
    }

    public bool VerifyAndOnline(string account, string clear_password, [MaybeNullWhen(false)] out IUserEntity entity)
    {
        UserEntity? res = null;

        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            res = new UserEntity()
            {
                Info = target,
                UserService = this,
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

    public bool Online(string account, NetworkToken clientToken)
    {
        if (OnlineUsers.ContainsKey(account))
        {
            return false;
        }
        var target = (from u in DB.UserTable where u.Account == account select u).FirstOrDefault();
        if (target is not null && target.IsActive)
        {
            OnlineUsers[account] = new()
            {
                Info = target,
                UserService = this,
                VerificationCode = Random.Shared.Next()
            };
            return true;
        }
        return false;
    }

    public bool Offline(string account)
    {
        if (OnlineUsers.TryGetValue(account, out var entity))
        {
            entity.IsOnline = false;
            return OnlineUsers.Remove(account);
        }
        return false;
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
#nullable enable
        public bool IsOnline
        {
            get; set;
        } = false;
        public NetworkToken? Token
        {
            get; set;
        }

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
