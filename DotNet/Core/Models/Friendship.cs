using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChatRoom.Core.Models;
#nullable disable
public class Friendship {
    public string UserAAccount {
        get;
        set;
    }
    public User UserA {
        get;
        set;
    }

    public string UserBAccount {
        get;
        set;
    }
    public User UserB {
        get;
        set;
    }

    [Required, DefaultValue(true)]
    public bool IsActive {
        get;
        set;
    }
    [Required]
    public DateTime CreatedTime {
        get;
        set;
    }
}