using IServiceProvider = ChatRoom.Core.Interface.IServiceProvider;

namespace ChatRoom.Core;

public interface IInjectable
{
    public void Initialize(IServiceProvider serviceProvider);
}