using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IMessage
{
    public void Serialize(dynamic json);

    public void Deserialize(dynamic json);
}