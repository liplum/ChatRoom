namespace ChatRoom.Core.Interface;
public interface IServiceProvider {
    public object Resolve(Type inType);
}

public static class ServiceProviderHelper {
    public static TIn Resolve<TIn>(this IServiceProvider provider) {
        return (TIn)provider.Resolve(typeof(TIn));
    }
}