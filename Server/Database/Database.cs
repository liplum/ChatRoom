using ChattingRoom.Server.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.DB;
public class Database : IDatabase
{
    private readonly object _dblock = new();
#nullable disable
    private CtrContext db;
#nullable enable
    public DbSet<User> UserTable => db.Users;

    public DbSet<ChatRoom> ChattingRoomTable => db.ChattingRooms;

    public DbSet<Membership> MembershipTable => db.Memberships;

    public DbContext Context => db;

    public void Connect()
    {
        lock (_dblock)
        {
            db = new();
        }
    }

    public void Disconnect()
    {
        lock (_dblock)
        {
            db?.Dispose();
        }
    }

    public void Initialize(IServiceProvider serviceProvider)
    {

    }

    public void SaveChange()
    {
        lock (_dblock)
        {
            db?.SaveChanges();
        }
    }
}