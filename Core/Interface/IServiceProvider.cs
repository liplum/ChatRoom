namespace ChattingRoom.Core;
public interface IServiceProvider
{
    public object Reslove(Type inType);
}

public static class ServiceProviderHelper
{
    public static In Reslove<In>(this IServiceProvider provider)
    {
        return (In)provider.Reslove(typeof(In));
    }
}
