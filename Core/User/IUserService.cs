namespace ChattingRoom.Core.Users;
public interface IUserService : IInjectable
{
    public UserID GenAvailableUserID();
    public void RegisterUser(UserID userID);
    public bool Verify(UserID id, string password);
}

public class UserService : IUserService
{
    public UserID GenAvailableUserID()
    {
        throw new NotImplementedException();
    }

    public void Initialize(IServiceProvider serviceProvider)
    {

    }

    public void RegisterUser(UserID userID)
    {
        throw new NotImplementedException();
    }

    public bool Verify(UserID id, string password)
    {
        throw new NotImplementedException();
    }
}