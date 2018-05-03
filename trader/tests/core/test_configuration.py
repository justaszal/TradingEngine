import pytest
import core.configuration as configuration
import importlib
from tests.test_utils.common import EmptyClass
from toolz import compose


class Test:
    pass


test_configuration_module = importlib.import_module(
    'tests.core.test_configuration')


@pytest.mark.parametrize('module, expected', [
    ('tests.core.test_configuration', test_configuration_module),
    ('tests.core.test_configuration1', None)
])
def test_load_module(module, expected):
    assert configuration.load_module(module) == expected


def test_load_module_classes():
    modules = configuration.load_module_classes(test_configuration_module)
    test_modues = filter(lambda module: module[0] == 'Test', modules)
    assert compose(len, list)(test_modues) == 1


@pytest.mark.parametrize('module, test_class, expected', [
    (test_configuration_module, Test, True),
    (test_configuration_module, EmptyClass, False)
])
def test_is_native_class(module, test_class, expected):
    assert configuration.is_native_class(module, test_class) == expected
