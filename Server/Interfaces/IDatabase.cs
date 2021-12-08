using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.Interfaces;
public interface IDatabase : IInjectable {

    public DbContext Context {
        get;
    }

    public DbSet<User> UserTable {
        get;
    }
    public DbSet<ChatRoom> ChatRoomTable {
        get;
    }
    public DbSet<Membership> MembershipTable {
        get;
    }
    public DbSet<Friendship> FriendshipTable {
        get;
    }
    public DbSet<FriendRequest> FriendRequestTable {
        get;
    }
    public DbSet<JoinRoomRequest> JoinRoomRequestTable {
        get;
    }
    public void Connect();

    public void Disconnect();

    public void SaveChange();
}