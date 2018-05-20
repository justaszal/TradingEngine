import importlib
import inspect
import pkgutil
from toolz import compose, curry, first


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


def load_price_handler_class(class_name, session_type):
    load_module = load_price_module(session_type=session_type)
    return compose(first, load_module_classes, load_module)(class_name)[1]


@curry
def load_price_module(module_name, session_type):
    price_handler_module = load_module(
        '.' + module_name, 'core.price_handler'
    )

    if price_handler_module is None:
        suffix = (session_type if session_type == 'live'
                  else 'historic')
        price_handler_module = load_module(
            '.' + module_name + '_' + suffix, 'core.price_handler'
        )

    return price_handler_module


def get_package_modules(package, ignore=None):
    modules = []

    for importer, modname, ispackage in pkgutil.iter_modules(package.__path__):
        if modname != ignore and not ispackage:
            modules.append(modname)

    return modules


def get_packages_modules(packages, ignore=False):
    modules = {}

    for package in packages:
        package_name = package.__name__.split('.')[-1] if ignore else None
        modules[package.__name__] = get_package_modules(package, package_name)

    return modules


def import_core_package(package):
    return importlib.import_module('core.' + package)


def get_algorithms():
    strategy_package = import_core_package('strategy')
    risk_manager_package = import_core_package('risk_manager')
    modules = get_packages_modules([strategy_package, risk_manager_package],
                                   True)

    return modules
