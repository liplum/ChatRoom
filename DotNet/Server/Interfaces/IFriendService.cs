using System.Diagnostics.CodeAnalysis;
using ChatRoom.Core;
using ChatRoom.Core.Models;

namespace ChatRoom.Server.Interfaces; 
public interface IFriendService :IInjectable {
    public bool HasFriendRequest(User from,User to,[NotNullWhen(true)] out FriendRequest? request);
    public bool AddFriendRequest(User from, User to, DateTime createdTime, out FriendRequest friendRequest);
    public FriendRequest[] GetAllFriendRequestsFrom(User from);
    public FriendRequest[] GetAllFriendRequestsTo(User to);
    
    public bool TryGetById(int reqId,[NotNullWhen(true)]  out FriendRequest? friendRequest);
    public void RemoveFriendRequest(FriendRequest friendRequest);
}