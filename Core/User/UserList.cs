namespace ChattingRoom.Core.Users;
public interface IUserList
{
    public void Load(IEnumerable<IUserEntity> users);
    public IUserEntity? this[string id] { get; }
    public void Add(IUserEntity user);
    public void Remove(string id);
}
public class UserList : IUserList
{
    private Dictionary<string, IUserEntity> _id2User = new();

    public void Load(IEnumerable<IUserEntity> users)
    {
        _id2User = new();
        foreach (var user in users)
        {
            _id2User[user.Account] = user;
        }
    }
    public IUserEntity? this[string id] => _id2User.TryGetValue(id, out var user) ? user : null;

    public void Add(IUserEntity user)
    {
        _id2User[user.Account] = user;
    }

    public void Remove(string id)
    {
        _id2User.Remove(id);
    }
}
