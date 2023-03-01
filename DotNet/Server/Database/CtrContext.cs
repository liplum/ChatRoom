using ChatRoom.Core.Models;
using ChatRoom.Core.Util;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace ChatRoom.Server.Database;
#nullable disable
public class CtrContext : DbContext {
    public CtrContext() {
        DbPath = "data.db".InRootDir();
    }
    public DbSet<User> Users {
        get;
        set;
    }
    public DbSet<Room> ChatRooms {
        get;
        set;
    }
    public DbSet<Membership> Memberships {
        get;
        set;
    }
    public DbSet<Friendship> Friendships {
        get;
        set;
    }
    public DbSet<FriendRequest> FriendRequests {
        get;
        set;
    }
    public DbSet<JoinRoomRequest> JoinRoomRequests {
        get;
        set;
    }
    public string DbPath {
        get;
        set;
    }

    protected override void OnConfiguring(DbContextOptionsBuilder options) {
        var con = new SqliteConnectionStringBuilder {
            DataSource = DbPath,
            Mode = SqliteOpenMode.ReadWriteCreate
        };
        options.UseSqlite(con.ToString());
    }
    protected override void OnModelCreating(ModelBuilder b) {
        base.OnModelCreating(b);
        b.Entity<Membership>()
            .HasKey(m => new { m.UserAccount, ChatRoomID = m.ChatRoomId });
        b.Entity<Membership>()
            .HasOne(m => m.User)
            .WithMany(user => user.Joined)
            .HasForeignKey(m => m.UserAccount);
        b.Entity<Membership>()
            .HasOne(m => m.Room)
            .WithMany(room => room.Members)
            .HasForeignKey(m => m.ChatRoomId);
        
        b.Entity<Friendship>()
            .HasKey(f => new { f.UserAAccount, f.UserBAccount });
        b.Entity<Friendship>()
            .HasOne(f => f.UserB)
            .WithMany(u => u.FriendOf)
            .HasForeignKey(f => f.UserBAccount)
            .OnDelete(DeleteBehavior.Restrict);
        b.Entity<Friendship>()
            .HasOne(f => f.UserA)
            .WithMany(u => u.Friends)
            .HasForeignKey(f => f.UserAAccount);
    }
}