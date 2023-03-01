using System.Diagnostics.CodeAnalysis;

namespace ChatRoom.Core.Interface;
public interface IServiceRegistry {
    /// <summary>
    ///     Registers a new singleton service.<br />
    ///     A singleton service can be constructed and initialized only once.<br />
    ///     Note that registering a singleton service with existed interface will override the old service.
    /// </summary>
    /// <param name="inType">the interface type which stands for key</param>
    /// <param name="outType">the class which implements the interface</param>
    public void RegisterSingleton(Type inType, Type outType);

    /// <summary>
    ///     Registers a new transient service.<br />
    ///     A transient service will be constructed and initialized every resolving. It's always a new object.<br />
    ///     Note that registering a transient service with existed interface will override the old service.
    /// </summary>
    /// <param name="inType">the interface type which stands for key</param>
    /// <param name="outType">the class which implements the interface</param>
    public void RegisterTransient(Type inType, Type outType);

    /// <summary>
    ///     Registers a instance.<br />
    ///     It can be not a <see cref="IInjectable" /> type. If it is,it will be initialized like a singleton.<br />
    ///     Note that registering a new instance with existed class will override the old instance.
    /// </summary>
    /// <param name="inType"></param>
    /// <param name="outType">the type</param>
    /// <param name="obj"></param>
    public void RegisterInstance(Type inType, Type outType, [NotNull] object obj);
}

public static class ServiceRegistryHelper {
    /// <summary>
    ///     Registers a new singleton service.<br />
    ///     A singleton service can be constructed and initialized only once.<br />
    ///     Note that registering a singleton service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="TIn">the interface type which stands for key</typeparam>
    /// <typeparam name="TOut">the class which implements the interface</typeparam>
    public static void RegisterSingleton<TIn, TOut>(this IServiceRegistry registry) where TIn : IInjectable where TOut : TIn, new() {
        registry.RegisterSingleton(typeof(TIn), typeof(TOut));
    }

    /// <summary>
    ///     Registers a new transient service.<br />
    ///     A transient service will be constructed and initialized every resolving. It's always a new object.<br />
    ///     Note that registering a transient service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="TIn">the interface type which stands for key</typeparam>
    /// <typeparam name="TOut">the class which implements the interface</typeparam>
    public static void RegisterTransient<TIn, TOut>(this IServiceRegistry registry) where TIn : IInjectable where TOut : TIn, new() {
        registry.RegisterTransient(typeof(TIn), typeof(TOut));
    }

    /// <summary>
    ///     Registers a instance.<br />
    ///     It can be not a <see cref="IInjectable" /> type. If it is,it will be initialized like a singleton.<br />
    ///     Note that registering a new instance with existed class will override the old instance.
    /// </summary>
    /// <typeparam name="TOut">the type</typeparam>
    /// <typeparam name="TIn"></typeparam>
    public static void RegisterInstance<TIn, TOut>(this IServiceRegistry registry, [NotNull] TOut obj) where TOut : notnull, TIn {
        registry.RegisterInstance(typeof(TIn), typeof(TOut), obj);
    }
}