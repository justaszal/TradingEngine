from toolz import pipe, curry
from functools import reduce


@curry
def mul(a, b):
    return a * b
