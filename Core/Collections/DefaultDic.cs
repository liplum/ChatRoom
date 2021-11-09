﻿using System.Collections;

namespace Liplum.Collections;

public class DefaultDic<TK, TV> : IDictionary<TK, TV> where TK : notnull
{
    private readonly Func<TK, TV>? _defaultGener;
    private readonly IDictionary<TK, TV>? _metadic;
    private readonly IDictionary<TK, TV> _inner;

    public DefaultDic([NotNull] IDictionary<TK, TV> metadic, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
    }

    public DefaultDic([NotNull] Func<TK, TV> defaultGener, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _defaultGener = defaultGener;
    }

    public DefaultDic([NotNull] IDictionary<TK, TV> metadic, [NotNull] Func<TK, TV> defaultGener, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _defaultGener = defaultGener;
    }

    public TV this[TK key]
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

    public ICollection<TK> Keys => _inner.Keys;

    public ICollection<TV> Values => _inner.Values;

    public int Count => _inner.Count;

    public bool IsReadOnly => ((IDictionary)_inner).IsReadOnly;

    public void Add(TK key, TV value)
    {
        _inner.Add(key, value);
    }

    public void Add(KeyValuePair<TK, TV> item)
    {
        _inner.Add(item);
    }

    public void Clear()
    {
        _inner.Clear();
    }

    public bool Contains(KeyValuePair<TK, TV> item)
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

    public bool ContainsKey(TK key)
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

    public void CopyTo(KeyValuePair<TK, TV>[] array, int arrayIndex)
    {
        _inner.CopyTo(array, arrayIndex);
    }

    public IEnumerator<KeyValuePair<TK, TV>> GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool Remove(TK key)
    {
        return _inner.Remove(key);
    }

    public bool Remove(KeyValuePair<TK, TV> item)
    {
        return _inner.Remove(item);
    }

    public bool TryGetValue(TK key, [MaybeNullWhen(false)] out TV value)
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
}

public class DefaultDic<TK, TV, TFrom> : IDictionary<TK, TV> where TK : notnull
{
    private readonly Func<TK, TV>? _defaultGener;
    private readonly IDictionary<TK, TFrom>? _metadic;
    private readonly IDictionary<TK, TV> _inner;
    private readonly Func<TFrom, TV>? _convert;

    public DefaultDic([NotNull] IDictionary<TK, TFrom> metadic, [NotNull] Func<TFrom, TV> convert, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _convert = convert;
    }

    public DefaultDic([NotNull] Func<TK, TV> defaultGener, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _defaultGener = defaultGener;
    }

    public DefaultDic([NotNull] IDictionary<TK, TFrom> metadic, [NotNull] Func<TFrom, TV> convert, [NotNull] Func<TK, TV> defaultGener, [AllowNull] Dictionary<TK, TV>? init = null)
    {
        if (init is null)
        {
            _inner = new Dictionary<TK, TV>();
        }
        else
        {
            _inner = init;
        }
        _metadic = metadic;
        _convert = convert;
        _defaultGener = defaultGener;
    }

    public TV this[TK key]
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

    public ICollection<TK> Keys => _inner.Keys;

    public ICollection<TV> Values => _inner.Values;

    public int Count => _inner.Count;

    public bool IsReadOnly => ((IDictionary)_inner).IsReadOnly;

    public void Add(TK key, TV value)
    {
        _inner.Add(key, value);
    }

    public void Add(KeyValuePair<TK, TV> item)
    {
        _inner.Add(item);
    }

    public void Clear()
    {
        _inner.Clear();
    }

    public bool Contains(KeyValuePair<TK, TV> item)
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

    public bool ContainsKey(TK key)
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

    public void CopyTo(KeyValuePair<TK, TV>[] array, int arrayIndex)
    {
        _inner.CopyTo(array, arrayIndex);
    }

    public IEnumerator<KeyValuePair<TK, TV>> GetEnumerator()
    {
        return _inner.GetEnumerator();
    }

    public bool Remove(TK key)
    {
        return _inner.Remove(key);
    }

    public bool Remove(KeyValuePair<TK, TV> item)
    {
        return _inner.Remove(item);
    }

    public bool TryGetValue(TK key, [MaybeNullWhen(false)] out TV value)
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
}