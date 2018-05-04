from toolz import curry


@curry
def append(arr, x):
    arr.append(x)
    return arr
