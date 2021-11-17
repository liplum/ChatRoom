using ChattingRoom.Core.DB.Models;

namespace ChattingRoom.Core.Users;
#nullable disable
public interface IUserEntity
{
    public string Account => Info.Account;

    public User Info
    {
        get;
    }

    public NetworkToken Token
    {
        get; set;
    }

    public void SaveChange();

    public bool IsOnline
    {
        get;
    }

    /// <summary>
    /// The verification code which will be changed every login.
    /// </summary>
    public int VerificationCode
    {
        get;
    }
}