global using ChattingRoom.Core.Users;
using ChattingRoom.Core.Messages;
using ChattingRoom.Core.Networks;

namespace ChattingRoom.Core;
public class ChattingRoom : IInjectable
{
    private IServer? Server { get; set; }
    private IMessageChannel? User { get; set; }
    private IMessageChannel? Chatting { get; set; }
    private IUserService? UserService { get; set; }

    private ILogger? Logger { get; set; }

    private INetwork? Network { get; set; }

    public ChattingRoom()
    {

    }

    public ChattingRoomID ID
    {
        get; set;
    }

    public void AddChattingItem(UserID sender, string chattingText, DateTime SendTimeClient)
    {
        Logger!.SendTip("Recevied a text.");
        Chatting!.SendMessage(Network!.AllConnectedClient,
            new ChattingMsg()
            {
                UserID = sender,
                SendTime = DateTime.UtcNow,
                ChattingText = chattingText,
                ChattingRoomID = ID
            });
    }

    public void Initialize(IServiceProvider serviceProvider)
    {
        Server = serviceProvider.Reslove<IServer>();
        Network = serviceProvider.Reslove<INetwork>();
        Logger = serviceProvider.Reslove<ILogger>();
        UserService = Server.UserService;
        User = Network.GetMessageChannelBy("User");
        Chatting = Network.GetMessageChannelBy("Chatting");
    }
}


public struct ChattingRoomID
{
    public readonly int ID;
    public ChattingRoomID(int id)
    {
        ID = id;
    }
    public override bool Equals([NotNullWhen(true)] object? obj)
    {
        return obj is ChattingRoomID o && ID == o.ID;
    }

    public static bool operator ==(ChattingRoomID left, ChattingRoomID right)
    {
        return left.Equals(right);
    }

    public static bool operator !=(ChattingRoomID left, ChattingRoomID right)
    {
        return !(left == right);
    }

    public override int GetHashCode()
    {
        return ID.GetHashCode();
    }

    public static explicit operator int(ChattingRoomID roomId)
    {
        return roomId.ID;
    }
    public static implicit operator ChattingRoomID(int roomId)
    {
        return new ChattingRoomID(roomId);
    }
}