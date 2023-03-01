using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
public class User {
    [Key, MaxLength(16)]
    [DatabaseGenerated(DatabaseGeneratedOption.None)]
    public string Account { get; set; }

    [Required, MaxLength(21)]
    public string Password { get; set; }
    [Required, MaxLength(16)]
    public string NickName { get; set; }
    [Required]
    public DateTime RegisterTime { get; set; }

    public DateTime? LastLoginTime { get; set; }

    public List<Membership> Joined { get; set; } = new();

    [Required, DefaultValue(true)]
    public bool IsActive { get; set; }

    [Required, DefaultValue(0)]
    public int CreatedRoomCount { get; set; }

    [Required, DefaultValue(0)]
    public int JoinedRoomCount { get; set; }
    public List<Friendship> Friends
    {
        get; set;
    } = new();
    public List<Friendship> FriendOf
    {
        get; set;
    } = new();
}