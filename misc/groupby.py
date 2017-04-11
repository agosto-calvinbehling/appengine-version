from collections import defaultdict


def groupby(data, key):
    result = defaultdict(list)
    for item in data:
        result[item[key]].append(item)
    return result


def multi_groupby(data, *keys):
    result = defaultdict(dict)
    last_idx = len(keys) - 1
    for item in data:
        inner = result
        for idx, key in enumerate(keys):
            if isinstance(key, basestring):
                value = item[key]
            else:
                value = item
                for key_value in key:
                    value = value[key_value]
            if idx < last_idx:
                inner.setdefault(value, {})
            else:
                inner.setdefault(value, [])
            inner = inner[value]
        inner.append(item)
    return result


def get_nested_value(dataDict, *keys, **kwargs):
    use_default = 'default' in kwargs
    default = kwargs.pop('default', None)
    try:
        for key in keys:
            dataDict = dataDict[key]
    except KeyError:
        if use_default:
            return default
        raise
    return dataDict


def multi_groupby_single_value(data, groupby_keys, result_key):
    result = defaultdict(dict)
    last_idx = len(groupby_keys) - 1
    for item in data:
        value = item[result_key] if isinstance(result_key, basestring) else get_nested_value(item, *result_key)

        partial_result = result
        for idx, key in enumerate(groupby_keys):
            key_value = item[key] if isinstance(key, basestring) else get_nested_value(*key)
            if idx < last_idx:
                partial_result.setdefault(key_value, {})
                partial_result = partial_result[key_value]
            else:
                partial_result[key_value] = value
    return result
