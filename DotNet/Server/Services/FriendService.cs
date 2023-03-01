using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core.Interface;
using ChatRoom.Core.Models;
using ChatRoom.Server.Interfaces;

namespace ChatRoom.Server.Services;

public class FriendService : IFriendService
{
#nullable disable
    private IDatabase DB { get; set; }
#nullable enable
    public void Initialize(IServiceProvider serviceProvider)
    {
        DB = serviceProvider.Resolve<IDatabase>();
    }

    public bool HasFriendRequest(User from, User to, [NotNullWhen(true)] out FriendRequest? request)
    {
        request = (from r in DB.FriendRequestTable where r.From == @from && r.To == to select r).FirstOrDefault();
        return request is not null;
    }

    public bool AddFriendRequest(User from, User to, DateTime createdTime, out FriendRequest friendRequest)
    {
        friendRequest = new()
        {
            From = from,
            To = to,
            Result = FriendRequestResult.None,
            CreatedTime = createdTime
        };
        DB.FriendRequestTable.Add(friendRequest);
        DB.SaveChange();
        return true;
    }

    public FriendRequest[] GetAllFriendRequestsFrom(User from)
    {
        return (from r in DB.FriendRequestTable where r.From == @from select r).ToArray();
    }

    public FriendRequest[] GetAllFriendRequestsTo(User to)
    {
        return (from r in DB.FriendRequestTable where r.To == to select r).ToArray();
    }

    public bool TryGetById(int reqId, [NotNullWhen(true)] out FriendRequest? friendRequest)
    {
        friendRequest = (from r in DB.FriendRequestTable where r.FriendRequestId == reqId select r).FirstOrDefault();
        return friendRequest is not null;
    }

    public void RemoveFriendRequest(FriendRequest friendRequest)
    {
        DB.FriendRequestTable.Remove(friendRequest);
        DB.SaveChange();
    }
}