from toolz import curry


@curry
def append(arr, x):
    arr.append(x)
    return arr


@curry
def set_attribute(obj, name, value):
    obj[name] = value
    return obj
