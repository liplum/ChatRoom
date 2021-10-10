namespace ChattingRoom.Core;
public interface IServiceRegistry
{
    /// <summary>
    /// Registers a new singleton service.<br/>
    /// A singleton service can be constructed and initialized only once.<br/>
    /// Note that registering a singleton service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="Interface">the interface type which stands for key</typeparam>
    /// <typeparam name="Clz">the class which implements the interface</typeparam>
    public void RegisterSingleton<Interface, Clz>() where Interface : IInjectable where Clz : Interface, new();

    /// <summary>
    /// Registers a new transient service.<br/>
    /// A transient service will be constructed and initialized every resolving. It's always a new object.<br/>
    /// Note that registering a transient service with existed interface will override the old service.
    /// </summary>
    /// <typeparam name="Interface">the interface type which stands for key</typeparam>
    /// <typeparam name="Clz">the class which implements the interface</typeparam>
    public void RegisterTransient<Interface, Clz>() where Interface : IInjectable where Clz : Interface, new();

    /// <summary>
    /// Registers a instance.<br/>
    /// It can be not a <see cref="IInjectable"/> type. If it is,it will be initialized like a singleton.<br/>
    /// Note that registering a new instance with existed class will override the old instance.
    /// </summary>
    /// <typeparam name="Clz">the type</typeparam>
    public void RegisterInstance<Clz>(Clz obj);
}
