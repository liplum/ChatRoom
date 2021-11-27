﻿using Microsoft.EntityFrameworkCore;

namespace ChattingRoom.Server.Interfaces;
public interface IDatabase : IInjectable
{
    public void Connect();

    public void Disconnect();

    public void SaveChange();

    public DbContext Context
    {
        get;
    }

    public DbSet<User> UserTable
    {
        get;
    }
    public DbSet<ChatRoom> ChatRoomTable
    {
        get;
    }
    public DbSet<Membership> MembershipTable
    {
        get;
    }
}