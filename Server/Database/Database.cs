using ChattingRoom.Server.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.DB;
public class Database : IDatabase
{
    private readonly object _dblock = new();
#nullable disable
    private CtrContext db;
#nullable enable
    public DbSet<User> UserTable
    {
        get
        {
            lock (_dblock)
            {
                return db.Users;
            }
        }
    }

    public DbSet<ChatRoom> ChatRoomTable
    {
        get
        {
            lock (_dblock)
            {
                return db.ChatRooms;
            }
        }
    }

    public DbSet<Membership> MembershipTable
    {
        get
        {
            lock (_dblock)
            {
                return db.Memberships;
            }
        }
    }

    public DbContext Context
    {
        get
        {
            lock (_dblock)
            {
                return db;
            }
        }
    }

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