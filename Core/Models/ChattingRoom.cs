using System.ComponentModel;

namespace ChattingRoom.Core.DB.Models;
#nullable disable
public class ChattingRoom
{
    public int ChattingRoomID
    {
        get; set;
    }

    public string Name
    {
        get; set;
    }

    public List<Membership> Members
    {
        get; set;
    } = new();


    [DefaultValue(true)]
    public bool IsActive
    {
        get; set;
    }
}