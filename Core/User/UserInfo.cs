using ChattingRoom.Core.Users.Securities;

namespace ChattingRoom.Core.Users;
public class UserInfo
{
    public UserID ID;
    public Password Password;
    public string UserName;

    public UserInfo(UserID id, Password password)
    {
        ID = id;
        Password = password;
        UserName = id.Name;
    }
}


