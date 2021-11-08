using System.Dynamic;

using Convrt = System.Convert;
namespace ChattingRoom.Server.Configs;


public class DataType
{
    public DataType([NotNull] Type type)
    {
        Type = type;
    }

    public Type Type
    {
        get; init;
    }

    public virtual object? Convert(object obj)
    {
        return Convrt.ChangeType(obj, Type);
    }

}

public class ConfigItemT
{
    public string Name
    {
        get; init;
    }
    public object DefaultValue
    {
        get; init;
    }
    public DataType DataType
    {
        get; init;
    }


    public ConfigItemT([NotNull] string name, [NotNull] object defaultValue)
    {
        Name = name;
        DefaultValue = defaultValue;
        DataType = new(defaultValue.GetType());

    }
    public ConfigItemT([NotNull] string name, [NotNull] object defaultValue, [NotNull] DataType dataType)
    {
        Name = name;
        DefaultValue = defaultValue;
        DataType = dataType;
    }
}

public class ConfigItemI
{
    public ConfigItemI([NotNull] ConfigItemT template, [NotNull] object value)
    {
        Template = template;
        Value = value;
    }

    public ConfigItemT Template
    {
        get; init;
    }
    public dynamic Value
    {
        get; init;
    }
}

public class Configurations : DynamicObject
{
    public readonly IDictionary<string, object> _jobj;
    public readonly IDictionary<string, ConfigItemT> _metadic;
    private readonly object _lock = new();
    public Configurations([NotNull] IDictionary<string, object> jobj, IDictionary<string, ConfigItemT> metadic)
    {
        _jobj = jobj;
        _metadic = metadic;
    }

    public bool TryGetValue(string key, out dynamic? result)
    {
        lock (_lock)
        {
            var dicJobj = _jobj!;
            if (dicJobj.TryGetValue(key, out result))
            {
                return true;
            }
            else if (_metadic.TryGetValue(key, out var configT))
            {
                var defaultV = configT.DefaultValue;
                dicJobj[key] = defaultV;
                result = defaultV;
                return true;
            }
            else
            {
                return false;
            }
        }
    }

    public override bool TryGetMember(GetMemberBinder binder, out object? result)
    {
        return TryGetValue(binder.Name, out result);
    }

    public override bool TryInvokeMember(InvokeMemberBinder binder, object?[]? args, out object? result)
    {
        if (args?.Length != 0)
        {
            throw new ArgumentException("Not allow argument.");
        }
        return TryGetValue(binder.Name, out result);
    }

    public override bool TryInvoke(InvokeBinder binder, object?[]? args, out object? result)
    {
        if (args is null || args.Length != 1 || (args.Length == 1 && args[0] is not string))
        {
            throw new ArgumentException($"Requires 1 {typeof(string).FullName} as argument.");
        }

        var keyName = (string)args[0]!;
        return TryGetValue(keyName, out result);
    }
    public override bool TrySetMember(SetMemberBinder binder, object? value)
    {
        if (value is null)
        {
            throw new ArgumentNullException(nameof(value));
        }
        var memberName = binder.Name;
        var dicJobj = _jobj!;
        lock (_lock)
        {
            dicJobj[memberName] = value;
        }
        return true;
    }
}