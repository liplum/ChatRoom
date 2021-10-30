using ChattingRoom.Core.Users;
using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Database;
public interface IUserDatabase
{
    public UserInfo? GetInfo([NotNull] UserID userID);

    public void SaveInfo([NotNull] UserInfo info);

    public void AddUser([NotNull] UserInfo info);

    public void RemoveUser([NotNull] UserID userID);
}
