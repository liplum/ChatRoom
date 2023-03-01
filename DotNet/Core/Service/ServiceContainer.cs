using System.Runtime.Serialization;
using ChatRoom.Core.Interface;
using IServiceProvider = ChatRoom.Core.Interface.IServiceProvider;

namespace ChatRoom.Core.Service;

public class ServiceContainer : IServiceProvider, IServiceRegistry
{
    private readonly Dictionary<Type, ServiceEntry> _allServices = new();
    public bool HotReload { get; set; } = false;

    public bool IsFrozen { get; private set; }

    private ServiceEntry this[Type type]
    {
        get
        {
            if (_allServices.TryGetValue(type, out var entry)) return entry;
            entry = new(type);
            _allServices[type] = entry;
            return entry;
        }
    }

    public object Resolve(Type inType)
    {
        if (!HotReload && !IsFrozen) throw new RegistryNotClosedYetException();
        object? returnValue = default;
        if (!_allServices.TryGetValue(inType, out var entry)) throw new ServiceNotRegisteredException(inType.Name);
        switch (entry.RegisterType)
        {
            case RegisterType.Singleton:
                ReturnInstance();
                break;
            case RegisterType.Instance:
                ReturnInstance();
                break;
            case RegisterType.Transient:
                ReturnTransient();
                break;
        }

        if (returnValue is not null) return returnValue;
        throw new ServiceNotRegisteredException(inType.Name);

        void ReturnInstance()
        {
            returnValue = entry.Instance!;
            if (!HotReload && entry.Injected) return;
            Inject(returnValue);
            entry.Injected = true;
        }

        void ReturnTransient()
        {
            var outType = entry.OutType;
            if (outType is not null)
            {
                returnValue = Activator.CreateInstance(outType)!;
                if (HotReload || !entry.Injected)
                {
                    Inject(returnValue);
                }
            }
            else
            {
                throw new ServiceResolveException(
                    $"Cannot resolve transient object {inType.FullName ?? inType.Name} because there is no corresponding out type.");
            }
        }
    }

    public void RegisterSingleton(Type inType, Type outType)
    {
        if (!HotReload && IsFrozen) throw new RegistryClosedException();
        var entry = this[inType];

        entry.Instance = Activator.CreateInstance(outType)!;
        entry.RegisterType = RegisterType.Singleton;
        entry.OutType = outType;
        entry.Injected = false;
    }

    public void RegisterTransient(Type inType, Type outType)
    {
        if (!HotReload && IsFrozen) throw new RegistryClosedException();
        var entry = this[inType];

        entry.RegisterType = RegisterType.Transient;
        entry.OutType = outType;
        entry.Injected = false;
    }

    public void RegisterInstance(Type inType, Type outType, object obj)
    {
        if (!HotReload && IsFrozen) throw new RegistryClosedException();

        if (obj is null) throw new ArgumentNullException(nameof(obj));
        var entry = this[inType];

        entry.Instance = obj;
        entry.RegisterType = RegisterType.Instance;
        entry.OutType = outType;
        entry.Injected = false;
    }

    public void Freeze()
    {
        IsFrozen = true;
    }

    private bool Inject(object obj)
    {
        if (obj is not IInjectable injectable) return false;
        injectable.Initialize(this);
        return true;
    }

    private class ServiceEntry
    {
        public ServiceEntry(Type inType)
        {
            InType = inType;
        }

        public Type InType { get; }
        public Type? OutType { get; set; }
        public object? Instance { get; set; }
        public RegisterType RegisterType { get; set; } = RegisterType.None;
        public bool Injected { get; set; }
    }

    private enum RegisterType
    {
        None,
        Singleton,
        Instance,
        Transient
    }
}

[Serializable]
public class ServiceNotRegisteredException : Exception
{
    public ServiceNotRegisteredException()
    {
    }

    public ServiceNotRegisteredException(string message) : base(message)
    {
    }

    public ServiceNotRegisteredException(string message, Exception inner) : base(message, inner)
    {
    }

    protected ServiceNotRegisteredException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class ServiceResolveException : Exception
{
    public ServiceResolveException()
    {
    }

    public ServiceResolveException(string message) : base(message)
    {
    }

    public ServiceResolveException(string message, Exception inner) : base(message, inner)
    {
    }

    protected ServiceResolveException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class RegistryClosedException : Exception
{
    public RegistryClosedException()
    {
    }

    public RegistryClosedException(string message) : base(message)
    {
    }

    public RegistryClosedException(string message, Exception inner) : base(message, inner)
    {
    }

    protected RegistryClosedException(SerializationInfo info, StreamingContext context) : base(info, context)
    {
    }
}

[Serializable]
public class RegistryNotClosedYetException : Exception
{
    public RegistryNotClosedYetException()
    {
    }

    public RegistryNotClosedYetException(string message) : base(message)
    {
    }

    public RegistryNotClosedYetException(string message, Exception inner) : base(message, inner)
    {
    }

    protected RegistryNotClosedYetException(
        SerializationInfo info,
        StreamingContext context) : base(info, context)
    {
    }
}