import yaml,json

def find_values_in_dict(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_values_in_dict(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find_values_in_dict(key, d):
                    yield result


def replace_in_json(obj, key, value):
    if isinstance(obj, dict):
        return {k: replace_in_json(v, key, value) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_in_json(elem, key, value) for elem in obj]
    elif obj==key:
       return value
    else:
        return obj


def convert_to_str(_input, enforce_str=True, encoding='utf-8'):
    if isinstance(_input, dict):
        return {convert_to_str(key, enforce_str=enforce_str, encoding=encoding): convert_to_str(value, enforce_str=enforce_str, encoding=encoding) for key, value in _input.iteritems()}
    elif isinstance(_input, list):
        return [convert_to_str(element, enforce_str=enforce_str, encoding=encoding) for element in _input]
    elif isinstance(_input, unicode):
        return _input.encode(encoding, 'replace')
    elif _input is not None and enforce_str:
        return str(_input)
    return _input


def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, dict):
        return {to_unicode_or_bust(key, encoding=encoding): to_unicode_or_bust(value, encoding=encoding) for key, value in obj.iteritems()}
    elif isinstance(obj, list):
        return [to_unicode_or_bust(element, encoding=encoding) for element in obj]
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj



def yaml_to_dict(yamldata):
    if not yamldata:
        return {}
    try:
        return yaml.load(yamldata)
    except:
        raise Exception(msg='Input data is not a valid yaml code.')


def dict_to_yaml(dictdata):
    if len(dictdata)==0:
        return ''
    else:
        try:
            return yaml.dump(yaml.load(json.dumps(dictdata)), indent=4, default_flow_style=False)
        except:
            raise Exception('Input data cannot be converted into a valid yaml code.')



def get_subdict(dict, fields):
    subdict = {}
    for field in fields:
        subdict[field]=dict[field]
    return subdict


def get_numeric_sorted_list(list, reversed=False):
    def numeric_compare(x, y):
        if not reversed:
            if (long(x)-long(y))>0:
                return 1
        elif (long(y)-long(x))>0:
            return 1
        return -1

    return sorted(list, cmp=numeric_compare)


def sync_dict1_with_dict2(dict1, dict2):
    l1 = [ k for k in dict1 if k not in dict2 ]
    l2 = [ k for k in dict2 if k not in dict1 ]
    for k1 in l1:
        del dict1[k1]
    for k2 in l2:
        dict1[k2]=dict2[k2]
    return dict1


def diff_dict_keys(dictA, dictB):
    l1 = [ k for k in dictA if k not in dictB ]
    l2 = [ k for k in dictB if k not in dictA ]
    list=l1+l2
    return list
