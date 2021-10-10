using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Services;
public class ServiceContainer : IServiceProvider, IServiceRegistry
{
    private readonly Dictionary<Type, ServiceEntry> _allServices = new();

    public Interface Reslove<Interface>()
    {
        var key = typeof(Interface);
        Interface? returnValue = default;
        if (_allServices.TryGetValue(key, out var entry))
        {
            switch (entry.RegisterType)
            {
                case RegisterType.Singleton:
                    ReturnIntance(entry);
                    break;
                case RegisterType.Instance:
                    ReturnIntance(entry);
                    break;
                case RegisterType.Transient:
                    ReturnTransient(entry);
                    break;
            }
            if (returnValue is not null)
            {
                return returnValue;
            }
        }
        throw new ServiceNotRegisteredException(key.Name);
        void ReturnIntance([NotNull] ServiceEntry entry)
        {
            returnValue = (Interface)entry.Instance!;
        }
        void ReturnTransient([NotNull] ServiceEntry entry)
        {
            returnValue = (Interface)Activator.CreateInstance(entry.Type)!;
            if (returnValue is IInjectable obj)
            {
                obj.Initialize(this);
            }
        }
    }

    public void RegisterSingleton<Interface, Clz>() where Interface : IInjectable where Clz : Interface, new()
    {
        var type = typeof(Interface);
        var entry = this[type];
        /*  if (entry.RegisterType != RegisterType.None)
          {
              throw new ServiceBeAlreadyRegisteredException(type.ToString());
          }*/
        entry.Instance = new Clz();
        entry.RegisterType = RegisterType.Singleton;
    }

    public void HandleReference()
    {
        foreach (var entry in _allServices.Values)
        {
            if (NeedHandle(entry))
            {
                if (entry.Instance is IInjectable obj)
                {
                    obj.Initialize(this);
                }
            }
        }

        static bool NeedHandle(ServiceEntry entry)
        {
            var registerType = entry.RegisterType;
            return registerType != RegisterType.None && registerType != RegisterType.Transient;
        }
    }

    public void RegisterTransient<Interface, Clz>() where Interface : IInjectable where Clz : Interface, new()
    {
        var type = typeof(Interface);
        var entry = this[type];
        /* if (entry.RegisterType != RegisterType.None)
         {
             throw new ServiceBeAlreadyRegisteredException(type.ToString());
         }*/
        entry.RegisterType = RegisterType.Transient;
    }

    public void RegisterInstance<Clz>(Clz obj)
    {
        var type = typeof(Clz);
        var entry = this[type];
        /* if (entry.RegisterType != RegisterType.None)
         {
             throw new ServiceBeAlreadyRegisteredException(type.ToString());
         }*/
        entry.Instance = obj;
        entry.RegisterType = RegisterType.Instance;
    }

    private ServiceEntry GetEntry([NotNull] Type type)
    {
        if (!_allServices.TryGetValue(type, out var entry))
        {
            entry = new(type);
            _allServices[type] = entry;
        }
        return entry;
    }

    private ServiceEntry this[[NotNull] Type type]
    {
        get => GetEntry(type);
    }

    internal class ServiceEntry
    {
        public ServiceEntry(Type type)
        {
            Type = type;
        }
        internal Type Type
        {
            get; init;
        }
        internal object? Instance
        {
            get; set;
        }
        internal RegisterType RegisterType
        {
            get; set;
        } = RegisterType.None;
    }

    internal enum RegisterType
    {
        None, Singleton, Instance, Transient
    }
}

[Serializable]
public class ServiceNotRegisteredException : Exception
{
    public ServiceNotRegisteredException()
    {
    }
    public ServiceNotRegisteredException(string message) : base(message) { }
    public ServiceNotRegisteredException(string message, Exception inner) : base(message, inner) { }
    protected ServiceNotRegisteredException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}


[Serializable]
public class ServiceBeAlreadyRegisteredException : Exception
{
    public ServiceBeAlreadyRegisteredException()
    {
    }
    public ServiceBeAlreadyRegisteredException(string message) : base(message) { }
    public ServiceBeAlreadyRegisteredException(string message, Exception inner) : base(message, inner) { }
    protected ServiceBeAlreadyRegisteredException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}