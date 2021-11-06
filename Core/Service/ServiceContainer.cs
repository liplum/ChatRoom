namespace ChattingRoom.Core.Services;
public class ServiceContainer : IServiceProvider, IServiceRegistry
{
    private readonly Dictionary<Type, ServiceEntry> _allServices = new();

    public In Reslove<In>()
    {
        var key = typeof(In);
        In? returnValue = default;
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
            returnValue = (In)entry.Instance!;
            Inject(returnValue);
        }
        void ReturnTransient([NotNull] ServiceEntry entry)
        {
            var outType = entry.OutType;
            var inType = entry.InType;
            if (outType is not null)
            {
                returnValue = (In)Activator.CreateInstance(outType)!;
                Inject(returnValue);
            }
            else
            {
                throw new ServiceResolveException($"Cannot reslove transient object {inType.FullName ?? inType.Name} because there is no corresponding out type.");
            }
        }

    }

    public void RegisterSingleton<In, Out>() where In : IInjectable where Out : In, new()
    {
        var inType = typeof(In);
        var entry = this[inType];

        var outType = typeof(Out);
        entry.Instance = new Out();
        entry.RegisterType = RegisterType.Singleton;
        entry.OutType = outType;
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

    public void RegisterTransient<In, Out>() where In : IInjectable where Out : In, new()
    {
        var inType = typeof(In);
        var entry = this[inType];

        var outType = typeof(Out);
        entry.RegisterType = RegisterType.Transient;
        entry.OutType = outType;
    }

    public void RegisterInstance<In, Out>([NotNull] Out obj) where Out : In
    {
        if (obj is null)
        {
            throw new ArgumentNullException(nameof(obj));
        }
        var inType = typeof(In);
        var entry = this[inType];

        var outType = typeof(Out);
        entry.Instance = obj;
        entry.RegisterType = RegisterType.Instance;
        entry.OutType = outType;
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

    public void Inject(IInjectable injectable)
    {
        injectable.Initialize(this);
    }

    public void Inject(object obj)
    {
        if (obj is IInjectable injectable)
        {
            Inject(injectable);
        }
    }

    private ServiceEntry this[[NotNull] Type type]
    {
        get => GetEntry(type);
    }

    private class ServiceEntry
    {
        public ServiceEntry(Type inType)
        {
            InType = inType;
        }
        public Type InType
        {
            get; init;
        }
        public Type? OutType
        {
            get; set;
        }
        public object? Instance
        {
            get; set;
        }
        public RegisterType RegisterType
        {
            get; set;
        } = RegisterType.None;
    }

    private enum RegisterType
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
public class ServiceResolveException : Exception
{
    public ServiceResolveException() { }
    public ServiceResolveException(string message) : base(message) { }
    public ServiceResolveException(string message, Exception inner) : base(message, inner) { }
    protected ServiceResolveException(
      System.Runtime.Serialization.SerializationInfo info,
      System.Runtime.Serialization.StreamingContext context) : base(info, context) { }
}