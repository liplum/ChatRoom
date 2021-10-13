using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface IMessage
{
    public void Serialize(dynamic json);

    public void Deserialize(dynamic json);
}

public interface IMessageHandler<in T> where T : IMessage
{

    public void Handle([NotNull] T msg, dynamic context);
}
