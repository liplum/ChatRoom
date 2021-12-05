using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
public enum FriendRequestResult {
    None = 0, Accept = 1, Refuse = 2, Dismiss = 3,
}

public class FriendRequest {
    [Key]
    public int FriendRequestId { get; set; }
    [Required]
    public User From { get; set; }
    [Required]
    public User To { get; set; }
    [Required]
    public DateTime CreatedTime { get; set; }
    [Required, DefaultValue(FriendRequestResult.None)]
    public FriendRequestResult Result { get; set; }
}