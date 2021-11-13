namespace ChattingRoom.Core;
public interface IServiceRegistry
{
    /// <summary>
    /// Registers a new singleton service.<br/>
    /// A singleton service can be constructed and initialized only once.<br/>
    /// Note that registering a singleton service with existed interface will override the old service.
    /// </summary>
    /// <param name="inType">the interface type which stands for key</param>
    /// <param name="outType">the class which implements the interface</typeparam>
    public void RegisterSingleton(Type inType, Type outType);

    /// <summary>
    /// Registers a new transient service.<br/>
    /// A transient service will be constructed and initialized every resolving. It's always a new object.<br/>
    /// Note that registering a transient service with existed interface will override the old service.
    /// </summary>
    /// <param name="inType">the interface type which stands for key</param>
    /// <param name="outType">the class which implements the interface</param>
    public void RegisterTransient(Type inType, Type outType);

    /// <summary>
    /// Registers a instance.<br/>
    /// It can be not a <see cref="IInjectable"/> type. If it is,it will be initialized like a singleton.<br/>
    /// Note that registering a new instance with existed class will override the old instance.
    /// </summary>
    /// <param name="outType">the type</param>
    public void RegisterInstance(Type inType, Type outType, [NotNull] object obj);
}

public static class ServiceRegistryHelper
{
    /// <summary>
    /// Registers a new singleton service.<br/>
    /// A singleton service can be constructed and initialized only once.<br/>
    /// Note that registering a singleton service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="In">the interface type which stands for key</typeparam>
    /// <typeparam name="Out">the class which implements the interface</typeparam>
    public static void RegisterSingleton<In, Out>(this IServiceRegistry registry) where In : IInjectable where Out : In, new()
    {
        registry.RegisterSingleton(typeof(In), typeof(Out));
    }

    /// <summary>
    /// Registers a new transient service.<br/>
    /// A transient service will be constructed and initialized every resolving. It's always a new object.<br/>
    /// Note that registering a transient service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="In">the interface type which stands for key</typeparam>
    /// <typeparam name="Out">the class which implements the interface</typeparam>
    public static void RegisterTransient<In, Out>(this IServiceRegistry registry) where In : IInjectable where Out : In, new()
    {
        registry.RegisterTransient(typeof(In), typeof(Out));
    }

    /// <summary>
    /// Registers a instance.<br/>
    /// It can be not a <see cref="IInjectable"/> type. If it is,it will be initialized like a singleton.<br/>
    /// Note that registering a new instance with existed class will override the old instance.
    /// </summary>
    /// <typeparam name="Out">the type</typeparam>
    public static void RegisterInstance<In, Out>(this IServiceRegistry registry, [NotNull] Out obj) where Out : notnull, In
    {
        registry.RegisterInstance(typeof(In), typeof(Out), obj);
    }
}