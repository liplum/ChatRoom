using ChattingRoom.Core.DB.Models;
using ChattingRoom.Core.Networks;

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
}