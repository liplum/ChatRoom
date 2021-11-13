namespace ChattingRoom.Server.Interfaces;
public interface IUserService : IInjectable
{
    public void RegisterUser(string account, string clear_password, DateTime registerTime);
    public bool Verify(string account, string clear_password, out IUserEntity? entity);

    public IUserEntity? ByAccount(string account);

    public bool DeleteUser(string account);

    public bool RecoverUser(string account);

    public bool NotOccupied(string account);
}
