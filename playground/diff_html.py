import sys
import json
import json_delta


def get_all_strings(elem):
    strings = []
    if isinstance(elem, list):
        for item in elem:
            strings.extend(get_all_strings(item))
    elif isinstance(elem, dict):
        for k, v in elem.items():
            strings.append(str(k))
            strings.extend(get_all_strings(v))
    else:
        strings.append(str(elem))
    return sorted(strings)


def sort_lists(elem):
    if isinstance(elem, list):
        return sorted((sort_lists(e) for e in elem),
                      key=lambda el: '\n'.join(get_all_strings(el)))
    if isinstance(elem, dict):
        return {k: sort_lists(v) for k, v in elem.items()}
    return elem


def read_data(path):
    with open(path) as f:
        # return json.dump  [json.loads(el) for el in f.read().split('--')]
        data = [json.loads(el) for el in f.read().split('--')]
        data = sort_lists(data)
        return json.dumps(data, indent=2, sort_keys=True)
    # txt = json.dumps(data, indent=2, sort_keys=True)


txt1 = read_data(sys.argv[1])

# tmp = json_delta.diff(read_data(sys.argv[1]), read_data(sys.argv[2]))
print(txt1)


# sys.argv[1] = 'test1.json'



# def obj_hook(dct):
# 	for k, v in dct:

#     if '__complex__' in dct:
#         return complex(dct['real'], dct['imag'])
#     return dct

# json.loads('{"__complex__": true, "real": 1, "imag": 2}',
#     object_hook=as_complex)
