namespace ChattingRoom.Core.Users;
public interface IUserList
{
    public void Load(IEnumerable<User> users);
    public void Persistence();
    public User? this[UserID id] { get; }
    public void Add(User user);
    public void Remove(UserID id);
}
public class UserList : IUserList
{
    private Dictionary<UserID, User> _id2User = new();

    public void Load(IEnumerable<User> users)
    {
        _id2User = new();
        foreach (var user in users)
        {
            _id2User[user.ID] = user;
        }
    }
    public User? this[UserID id]
    {
        get => _id2User.TryGetValue(id, out var user) ? user : null;
    }

    public void Persistence()
    {

    }

    public void Add(User user)
    {
        _id2User[user.ID] = user;
    }

    public void Remove(UserID id)
    {
        _id2User.Remove(id);
    }
}
