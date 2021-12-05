using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
public class ChatRoom {
    [Key] public int ChatRoomId { get; set; }
    [Required] [MaxLength(16)] public string Name { get; set; }

    public List<Membership> Members { get; set; } = new();


    [Required] [DefaultValue(true)] public bool IsActive { get; set; }

    [Required] [DefaultValue(0)] public int MemberCount { get; set; }

    [Required] public DateTime CreatedTime { get; set; }
}