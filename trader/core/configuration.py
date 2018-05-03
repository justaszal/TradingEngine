import importlib
import inspect
from toolz import curry


def load_module(path, package=None):
    try:
        module = importlib.import_module(path, package)
    except ModuleNotFoundError:
        module = None

    return module


def load_module_classes(module):
    is_module_class = is_native_class(module)
    return inspect.getmembers(module, is_module_class)


@curry
def is_native_class(module, cls):
    cls_module = inspect.getmodule(cls)
    module = inspect.getmodule(module)
    return inspect.isclass(cls) and cls_module.__file__ == module.__file__
