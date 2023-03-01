using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChatRoom.Core.Models;
#nullable disable
[DefaultValue(None)]
public enum MemberType {
    None = 0,
    Member = 1,
    Owner = 2,
    Admin = 3,
}

public class Membership {
    public int ChatRoomId { get; set; }

    public string UserAccount { get; set; }

    public User User { get; set; }
    [Required, DefaultValue(MemberType.None)]
    public MemberType Type { get; set; }

    public ChatRoom ChatRoom { get; set; }

    [Required, DefaultValue(true)]
    public bool IsActive { get; set; }

    [Required]
    public DateTime CreatedTime { get; set; }
}