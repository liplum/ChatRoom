using System.Runtime.Serialization;

namespace ChattingRoom.Core.Services;
public class ServiceContainer : IServiceProvider, IServiceRegistry {
    private readonly Dictionary<Type, ServiceEntry> _allServices = new();
    public bool HotReload {
        get;
        set;
    } = false;

    public bool Closed {
        get;
        private set;
    }

    private ServiceEntry this[[NotNull] Type type] {
        get {
            if (!_allServices.TryGetValue(type, out var entry)) {
                entry = new(type);
                _allServices[type] = entry;
            }
            return entry;
        }
    }

    public object Resolve(Type inType) {
        if (!HotReload && !Closed) throw new RegistryNotClosedYetException();
        object? returnValue = default;
        if (_allServices.TryGetValue(inType, out var entry)) {
            switch (entry.RegisterType) {
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
            if (returnValue is not null) return returnValue;
        }
        throw new ServiceNotRegisteredException(inType.Name);
        void ReturnIntance([NotNull] ServiceEntry entry) {
            returnValue = entry.Instance!;
            if (HotReload || !entry.Injected) {
                Inject(returnValue);
                entry.Injected = true;
            }
        }
        void ReturnTransient([NotNull] ServiceEntry entry) {
            var outType = entry.OutType;
            var inType = entry.InType;
            if (outType is not null) {
                returnValue = Activator.CreateInstance(outType)!;
                if (HotReload || !entry.Injected) {
                    Inject(returnValue);
                    entry.Injected = true;
                }
            }
            else {
                throw new ServiceResolveException($"Cannot reslove transient object {inType.FullName ?? inType.Name} because there is no corresponding out type.");
            }
        }

    }

    public void RegisterSingleton(Type inType, Type outType) {
        if (!HotReload && Closed) throw new RegistryClosedException();
        var entry = this[inType];

        entry.Instance = Activator.CreateInstance(outType)!;
        entry.RegisterType = RegisterType.Singleton;
        entry.OutType = outType;
    }

    public void RegisterTransient(Type inType, Type outType) {
        if (!HotReload && Closed) throw new RegistryClosedException();
        var entry = this[inType];

        entry.RegisterType = RegisterType.Transient;
        entry.OutType = outType;
    }

    public void RegisterInstance(Type inType, Type outType, [NotNull] object obj) {
        if (!HotReload && Closed) throw new RegistryClosedException();

        if (obj is null) throw new ArgumentNullException(nameof(obj));
        var entry = this[inType];

        entry.Instance = obj;
        entry.RegisterType = RegisterType.Instance;
        entry.OutType = outType;
    }

    public void Close() {
        Closed = true;
    }


    public void HandleReference() {
        foreach (var entry in _allServices.Values)
            if (NeedHandle(entry))
                if (entry.Instance is IInjectable obj)
                    obj.Initialize(this);

        static bool NeedHandle(ServiceEntry entry) {
            var registerType = entry.RegisterType;
            return registerType != RegisterType.None && registerType != RegisterType.Transient;
        }
    }

    private bool Inject(object obj) {
        if (obj is IInjectable injectable) {
            injectable.Initialize(this);
            return true;
        }
        return false;
    }

    private class ServiceEntry {
        public ServiceEntry(Type inType) {
            InType = inType;
        }
        public Type InType {
            get;
        }
        public Type? OutType {
            get;
            set;
        }
        public object? Instance {
            get;
            set;
        }
        public RegisterType RegisterType {
            get;
            set;
        } = RegisterType.None;
        public bool Injected {
            get;
            set;
        }
    }

    private enum RegisterType {
        None, Singleton, Instance, Transient
    }
}

[Serializable]
public class ServiceNotRegisteredException : Exception {
    public ServiceNotRegisteredException() {
    }
    public ServiceNotRegisteredException(string message) : base(message) { }
    public ServiceNotRegisteredException(string message, Exception inner) : base(message, inner) { }
    protected ServiceNotRegisteredException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}

[Serializable]
public class ServiceResolveException : Exception {
    public ServiceResolveException() {
    }
    public ServiceResolveException(string message) : base(message) { }
    public ServiceResolveException(string message, Exception inner) : base(message, inner) { }
    protected ServiceResolveException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}

[Serializable]
public class RegistryClosedException : Exception {
    public RegistryClosedException() {
    }
    public RegistryClosedException(string message) : base(message) { }
    public RegistryClosedException(string message, Exception inner) : base(message, inner) { }
    protected RegistryClosedException(SerializationInfo info, StreamingContext context) : base(info, context) { }
}

[Serializable]
public class RegistryNotClosedYetException : Exception {
    public RegistryNotClosedYetException() {
    }
    public RegistryNotClosedYetException(string message) : base(message) { }
    public RegistryNotClosedYetException(string message, Exception inner) : base(message, inner) { }
    protected RegistryNotClosedYetException(
        SerializationInfo info,
        StreamingContext context) : base(info, context) {
    }
}