from toolz import pipe
from .predicate import (is_dict, is_list)


def get_defined_dict_values(x):
    if is_dict(x):
        return {k: v for (k, v) in x.items() if v is not None}
    return {}


def get_defined_list_values(x):
    if is_list(x):
        return filter(lambda y: y is not None, x)
    return []
