using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
[DefaultValue(None)]
public enum MemberType {
    None,
    Member,
    Owner,
    Admin
}

public class Membership {
    public int ChatRoomId { get; set; }

    public string UserAccount { get; set; }

    public User User { get; set; }

    public MemberType Type { get; set; }

    public ChatRoom ChatRoom { get; set; }

    [Required] [DefaultValue(true)] public bool IsActive { get; set; }

    [Required] public DateTime CreatedTime { get; set; }
}