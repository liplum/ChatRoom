using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.DB;
#nullable disable
public class CtrContext : DbContext
{
    public DbSet<User> Users
    {
        get; set;
    }
    public DbSet<ChatRoom> ChatRooms
    {
        get; set;
    }

    public DbSet<Membership> Memberships
    {
        get; set;
    }

    public string DbPath
    {
        get; set;
    }
    public CtrContext()
    {
        DbPath = "data.db".InRootDir();
    }

    protected override void OnConfiguring(DbContextOptionsBuilder options)
    {
        var con = new SqliteConnectionStringBuilder()
        {
            DataSource = DbPath,
            Mode = SqliteOpenMode.ReadWriteCreate
        };
        options.UseSqlite(con.ToString());
    }
    protected override void OnModelCreating(ModelBuilder b)
    {
        base.OnModelCreating(b);
        b.Entity<Membership>()
            .HasKey(m => new { m.UserAccount, m.ChatRoomID });
        b.Entity<Membership>()
            .HasOne(m => m.User)
            .WithMany(user => user.Joined)
            .HasForeignKey(m => m.UserAccount);
        b.Entity<Membership>()
            .HasOne(m => m.ChatRoom)
            .WithMany(room => room.Members)
            .HasForeignKey(m => m.ChatRoomID);
    }
}