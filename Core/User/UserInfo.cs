using ChattingRoom.Core.Users.Securities;

namespace ChattingRoom.Core.Users;
public class UserInfo
{
    public UserID ID;
    public Password Password;
    public string NickName;

    public UserInfo(UserID id, Password password, string nickName)
    {
        ID = id;
        Password = password;
        NickName = nickName;
    }
}
