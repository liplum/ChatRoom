using System.Collections;
using System.Dynamic;

namespace Liplum.Collections;

public class DefaultObj<TV> : DynamicObject, IDictionary<string, TV>
{
    private readonly Func<string, TV>? _defaultGener;
    private readonly IDictionary<string, TV>? _metadic;
    private readonly IDictionary<string, TV> _inner;

    public DefaultObj([NotNull] IDictionary<string, TV> metadic, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
    }

    public DefaultObj([NotNull] Func<string, TV> defaultGener, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _defaultGener = defaultGener;
    }

    public DefaultObj([NotNull] IDictionary<string, TV> metadic, [NotNull] Func<string, TV> defaultGener, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _defaultGener = defaultGener;
    }

    public TV this[string key]
    {
        get
        {
            if (_inner.TryGetValue(key, out var value))
            {
                return value;
            }
            else if (_metadic is not null && _metadic.TryGetValue(key, out var metavalue))
            {
                _inner[key] = metavalue;
                return metavalue;
            }
            else if (_defaultGener is not null)
            {
                var genedValue = _defaultGener(key);
                _inner[key] = genedValue;
                return genedValue;
            }
            else
            {
                throw new KeyNotFoundException(key.ToString());
            }
        }
        set => _inner[key] = value;
    }

    public ICollection<string> Keys => _inner.Keys;

    public ICollection<TV> Values => _inner.Values;

    public int Count => _inner.Count;

    public bool IsReadOnly => ((IDictionary)_inner).IsReadOnly;

    public void Add(string key, TV value)
    {
        _inner.Add(key, value);
    }

    public void Add(KeyValuePair<string, TV> item)
    {
        _inner.Add(item);
    }

    public void Clear()
    {
        _inner.Clear();
    }

    public bool Contains(KeyValuePair<string, TV> item)
    {
        var key = item.Key;
        var v = item.Value;
        if (_inner.Contains(item))
        {
            return true;
        }
        else if (_metadic is not null && _metadic.TryGetValue(key, out var value))
        {
            if (Equals(value, v))
            {
                _inner[key] = value;
                return true;
            }
            else
            {
                return false;
            }
        }
        else if (_defaultGener is not null)
        {
            var genedValue = _defaultGener(key);
            if (Equals(genedValue, _defaultGener))
            {
                _inner[key] = genedValue;
                return true;
            }
            else
            {
                return false;
            }
        }
        else
        {
            return false;
        }
    }

    public bool ContainsKey(string key)
    {
        if (_inner.ContainsKey(key))
        {
            return true;
        }
        else if (_metadic is not null && _metadic.TryGetValue(key, out var value))
        {
            _inner[key] = value;
            return true;
        }
        else if (_defaultGener is not null)
        {
            var genedValue = _defaultGener(key);
            _inner[key] = genedValue;
            return true;
        }
        else
        {
            return false;
        }
    }

    public void CopyTo(KeyValuePair<string, TV>[] array, int arrayIndex)
    {
        _inner.CopyTo(array, arrayIndex);
    }

    public IEnumerator<KeyValuePair<string, TV>> GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool Remove(string key)
    {
        return _inner.Remove(key);
    }

    public bool Remove(KeyValuePair<string, TV> item)
    {
        return _inner.Remove(item);
    }

    public bool TryGetValue(string key, [MaybeNullWhen(false)] out TV value)
    {

        if (_inner.TryGetValue(key, out value))
        {
            return true;
        }
        else if (_metadic is not null && _metadic.TryGetValue(key, out value))
        {
            _inner[key] = value;
            return true;
        }
        else if (_defaultGener is not null)
        {
            value = _defaultGener(key);
            _inner[key] = value;
            return true;
        }
        else
        {
            return false;
        }
    }

    IEnumerator IEnumerable.GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool TryGetMember(string name, out object? result)
    {
        var b = TryGetValue(name, out var res);
        result = res;
        return b;
    }
    public override bool TryGetMember(GetMemberBinder binder, out object? result)
    {
        var name = binder.Name;
        return TryGetMember(binder.Name, out result);
    }

    public override bool TryInvokeMember(InvokeMemberBinder binder, object?[]? args, out object? result)
    {
        if (args?.Length != 0)
        {
            throw new ArgumentException("Not allow argument.");
        }
        return TryGetMember(binder.Name, out result);
    }

    public override bool TryInvoke(InvokeBinder binder, object?[]? args, out object? result)
    {
        if (args is null || args.Length != 1 || (args.Length == 1 && args[0] is not string))
        {
            throw new ArgumentException($"Requires 1 {typeof(string).FullName} as argument.");
        }

        var keyName = (string)args[0]!;
        return TryGetMember(keyName, out result);
    }
    public override bool TrySetMember(SetMemberBinder binder, object? value)
    {
        if (value is TV v)
        {
            var memberName = binder.Name;
            _inner[memberName] = v;
            return true;
        }
        return false;
    }
}

public class DefaultObj<TV, TFrom> : DynamicObject, IDictionary<string, TV>
{
    private readonly Func<string, TV>? _defaultGener;
    private readonly IDictionary<string, TFrom>? _metadic;
    private readonly IDictionary<string, TV> _inner;
    private readonly Func<TFrom, TV>? _convert;

    public DefaultObj([NotNull] IDictionary<string, TFrom> metadic, [NotNull] Func<TFrom, TV> convert, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _convert = convert;
    }

    public DefaultObj([NotNull] Func<string, TV> defaultGener, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _defaultGener = defaultGener;
    }

    public DefaultObj([NotNull] IDictionary<string, TFrom> metadic, [NotNull] Func<TFrom, TV> convert, [NotNull] Func<string, TV> defaultGener, [AllowNull] Dictionary<string, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<string, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _defaultGener = defaultGener;
        _convert = convert;
    }

    public TV this[string key]
    {
        get
        {
            if (_inner.TryGetValue(key, out var value))
            {
                return value;
            }
            else if (_metadic is not null && _convert is not null && _metadic.TryGetValue(key, out var metavalue))
            {
                var finalValue = _convert(metavalue);
                _inner[key] = finalValue;
                return finalValue;
            }
            else if (_defaultGener is not null)
            {
                var genedValue = _defaultGener(key);
                _inner[key] = genedValue;
                return genedValue;
            }
            else
            {
                throw new KeyNotFoundException(key.ToString());
            }
        }
        set => _inner[key] = value;
    }

    public ICollection<string> Keys => _inner.Keys;

    public ICollection<TV> Values => _inner.Values;

    public int Count => _inner.Count;

    public bool IsReadOnly => ((IDictionary)_inner).IsReadOnly;

    public void Add(string key, TV value)
    {
        _inner.Add(key, value);
    }

    public void Add(KeyValuePair<string, TV> item)
    {
        _inner.Add(item);
    }

    public void Clear()
    {
        _inner.Clear();
    }

    public bool Contains(KeyValuePair<string, TV> item)
    {
        var key = item.Key;
        var v = item.Value;
        if (_inner.Contains(item))
        {
            return true;
        }
        else if (_metadic is not null && _convert is not null && _metadic.TryGetValue(key, out var metavalue))
        {
            var finalValue = _convert(metavalue);
            if (Equals(finalValue, v))
            {
                _inner[key] = finalValue;
                return true;
            }
            else
            {
                return false;
            }
        }
        else if (_defaultGener is not null)
        {
            var genedValue = _defaultGener(key);
            if (Equals(genedValue, _defaultGener))
            {
                _inner[key] = genedValue;
                return true;
            }
            else
            {
                return false;
            }
        }
        else
        {
            return false;
        }
    }

    public bool ContainsKey(string key)
    {
        if (_inner.ContainsKey(key))
        {
            return true;
        }
        else if (_metadic is not null && _convert is not null && _metadic.TryGetValue(key, out var metavalue))
        {
            var finalValue = _convert(metavalue);
            _inner[key] = finalValue;
            return true;
        }
        else if (_defaultGener is not null)
        {
            var genedValue = _defaultGener(key);
            _inner[key] = genedValue;
            return true;
        }
        else
        {
            return false;
        }
    }

    public void CopyTo(KeyValuePair<string, TV>[] array, int arrayIndex)
    {
        _inner.CopyTo(array, arrayIndex);
    }

    public IEnumerator<KeyValuePair<string, TV>> GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool Remove(string key)
    {
        return _inner.Remove(key);
    }

    public bool Remove(KeyValuePair<string, TV> item)
    {
        return _inner.Remove(item);
    }

    public bool TryGetValue(string key, [MaybeNullWhen(false)] out TV value)
    {

        if (_inner.TryGetValue(key, out value))
        {
            return true;
        }
        else if (_metadic is not null && _convert is not null && _metadic.TryGetValue(key, out var metavalue))
        {
            var finalValue = _convert(metavalue);
            _inner[key] = finalValue;
            value = finalValue;
            return true;
        }
        else if (_defaultGener is not null)
        {
            value = _defaultGener(key);
            _inner[key] = value;
            return true;
        }
        else
        {
            return false;
        }
    }

    IEnumerator IEnumerable.GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool TryGetMember(string name, out object? result)
    {
        var b = TryGetValue(name, out var res);
        result = res;
        return b;
    }
    public override bool TryGetMember(GetMemberBinder binder, out object? result)
    {
        var name = binder.Name;
        return TryGetMember(binder.Name, out result);
    }

    public override bool TryInvokeMember(InvokeMemberBinder binder, object?[]? args, out object? result)
    {
        if (args?.Length != 0)
        {
            throw new ArgumentException("Not allow argument.");
        }
        return TryGetMember(binder.Name, out result);
    }

    public override bool TryInvoke(InvokeBinder binder, object?[]? args, out object? result)
    {
        if (args is null || args.Length != 1 || (args.Length == 1 && args[0] is not string))
        {
            throw new ArgumentException($"Requires 1 {typeof(string).FullName} as argument.");
        }

        var keyName = (string)args[0]!;
        return TryGetMember(keyName, out result);
    }
    public override bool TrySetMember(SetMemberBinder binder, object? value)
    {
        if (value is TV v)
        {
            var memberName = binder.Name;
            _inner[memberName] = v;
            return true;
        }
        return false;
    }
}
