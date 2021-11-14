﻿using System.ComponentModel;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
[DefaultValue(None)]
public enum MemberType
{
    None, Member, Owner, Admin
}

public class Membership
{
    public int ChattingRoomID
    {
        get; set;
    }

    public string UserAccount
    {
        get; set;
    }

    public User User
    {
        get; set;
    }
    public MemberType Type
    {
        get; set;
    }
    public ChattingRoom ChattingRoom
    {
        get; set;
    }

    [DefaultValue(true)]
    public bool IsActive
    {
        get; set;
    }
}