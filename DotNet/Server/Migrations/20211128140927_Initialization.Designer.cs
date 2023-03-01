﻿// <auto-generated />
using System;
using ChattingRoom.Server.DB;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

#nullable disable

namespace ChattingRoom.Server.Migrations
{
    [DbContext(typeof(CtrContext))]
    [Migration("20211128140927_Initialization")]
    partial class Initialization
    {
        protected override void BuildTargetModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder.HasAnnotation("ProductVersion", "6.0.0");

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.ChatRoom", b =>
                {
                    b.Property<int>("ChatRoomID")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("CreatedTime")
                        .HasColumnType("TEXT");

                    b.Property<bool>("IsActive")
                        .HasColumnType("INTEGER");

                    b.Property<int>("MemberCount")
                        .HasColumnType("INTEGER");

                    b.Property<string>("Name")
                        .IsRequired()
                        .HasMaxLength(16)
                        .HasColumnType("TEXT");

                    b.HasKey("ChatRoomID");

                    b.ToTable("ChatRooms");
                });

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.Membership", b =>
                {
                    b.Property<string>("UserAccount")
                        .HasColumnType("TEXT");

                    b.Property<int>("ChatRoomID")
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("CreatedTime")
                        .HasColumnType("TEXT");

                    b.Property<bool>("IsActive")
                        .HasColumnType("INTEGER");

                    b.Property<int>("Type")
                        .HasColumnType("INTEGER");

                    b.HasKey("UserAccount", "ChatRoomID");

                    b.HasIndex("ChatRoomID");

                    b.ToTable("Memberships");
                });

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.User", b =>
                {
                    b.Property<string>("Account")
                        .HasMaxLength(16)
                        .HasColumnType("TEXT");

                    b.Property<int>("CreatedRoomCount")
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsActive")
                        .HasColumnType("INTEGER");

                    b.Property<int>("JoinedRoomCount")
                        .HasColumnType("INTEGER");

                    b.Property<DateTime?>("LastLoginTime")
                        .HasColumnType("TEXT");

                    b.Property<string>("NickName")
                        .IsRequired()
                        .HasMaxLength(16)
                        .HasColumnType("TEXT");

                    b.Property<string>("Password")
                        .IsRequired()
                        .HasMaxLength(21)
                        .HasColumnType("TEXT");

                    b.Property<DateTime>("RegisterTime")
                        .HasColumnType("TEXT");

                    b.HasKey("Account");

                    b.ToTable("Users");
                });

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.Membership", b =>
                {
                    b.HasOne("ChattingRoom.Core.DB.Models.ChatRoom", "ChatRoom")
                        .WithMany("Members")
                        .HasForeignKey("ChatRoomID")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ChattingRoom.Core.DB.Models.User", "User")
                        .WithMany("Joined")
                        .HasForeignKey("UserAccount")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("ChatRoom");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.ChatRoom", b =>
                {
                    b.Navigation("Members");
                });

            modelBuilder.Entity("ChattingRoom.Core.DB.Models.User", b =>
                {
                    b.Navigation("Joined");
                });
#pragma warning restore 612, 618
        }
    }
}
