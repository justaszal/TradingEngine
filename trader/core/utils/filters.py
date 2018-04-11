from toolz import pipe
from .predicate import (is_dict, is_list)


def get_defined_dict_values(x):
    if is_dict(x):
        return {k: v for (k, v) in x.items() if v is not None}
    return None


def get_defined_list_values(x):
    if is_list(x):
        return pipe(
            x,
            lambda l: filter(lambda y: y is not None, l),
            list
        )
    return None
