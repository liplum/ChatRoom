namespace ChattingRoom.Core.Users;
public class UserList
{
    private Dictionary<UserID, User> _id2User = new();

    private void Load(IEnumerable<User> users)
    {

    }
}
