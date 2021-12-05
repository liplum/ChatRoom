using ChattingRoom.Server.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.DB;
public class Database : IDatabase {
    private readonly object _dbLock = new();
#nullable disable
    private CtrContext _db;
#nullable enable
    public DbSet<User> UserTable {
        get {
            lock (_dbLock) {
                return _db.Users;
            }
        }
    }

    public DbSet<ChatRoom> ChatRoomTable {
        get {
            lock (_dbLock) {
                return _db.ChatRooms;
            }
        }
    }

    public DbSet<Membership> MembershipTable {
        get {
            lock (_dbLock) {
                return _db.Memberships;
            }
        }
    }

    public DbContext Context {
        get {
            lock (_dbLock) {
                return _db;
            }
        }
    }

    public void Connect() {
        lock (_dbLock) {
            _db = new();
        }
    }

    public void Disconnect() {
        lock (_dbLock) {
            _db?.Dispose();
        }
    }

    public void Initialize(IServiceProvider serviceProvider) {

    }

    public void SaveChange() {
        lock (_dbLock) {
            _db?.SaveChanges();
        }
    }
}