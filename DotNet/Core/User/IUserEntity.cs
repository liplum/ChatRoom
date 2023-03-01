using ChatRoom.Core.Network;

namespace ChatRoom.Core.User;
#nullable disable
public interface IUserEntity {
    public string Account => Info.Account;

    public Models.User Info {
        get;
    }

    public NetworkToken Token {
        get;
        set;
    }

    public bool IsOnline {
        get;
    }

    /// <summary>
    ///     The verification code which will be changed every login.
    /// </summary>
    public int VerificationCode {
        get;
    }

    public void SaveChange();
}