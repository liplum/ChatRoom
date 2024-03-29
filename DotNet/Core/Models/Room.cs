﻿using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace ChatRoom.Core.Models;
#nullable disable
public class Room
{
    [Key] public int ChatRoomId { get; set; }
    [Required, MaxLength(16)] public string Name { get; set; }

    public List<Membership> Members { get; set; } = new();


    [Required, DefaultValue(true)] public bool IsActive { get; set; }

    [Required, DefaultValue(0)] public int MemberCount { get; set; }

    [Required] public DateTime CreatedTime { get; set; }
}