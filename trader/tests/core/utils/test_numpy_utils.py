import pytest
import core.utils.numpy_utils as np_utils
import numpy as np


def nan_equal(a, b):
    try:
        np.testing.assert_equal(a, b)
    except AssertionError:
        return False
    return True


@pytest.mark.parametrize('arr, shift, expected', [
    (
        np.array([0, 1, 2], dtype=np.float), 2,
        np.array([np.nan, np.nan, 0], dtype=np.float)
    ),
    (
        np.ndarray((2,), buffer=np.array([1, 2], dtype=np.float)), 1,
        np.ndarray((2,), buffer=np.array([np.nan, 1], dtype=np.float))
    )
])
def test_shift_right(arr, shift, expected):
    np_utils.shift(arr, shift)
    assert nan_equal(arr, expected)


@pytest.mark.parametrize('arr, shift, expected', [
    (
        np.array([0, 1, 2], dtype=np.float), -2,
        np.array([2, np.nan, np.nan], dtype=np.float)
    ),
    (
        np.ndarray((2,), buffer=np.array([1, 2], dtype=np.float)), -1,
        np.ndarray((2,), buffer=np.array([2, np.nan], dtype=np.float))
    )
])
def test_shift_left(arr, shift, expected):
    np_utils.shift(arr, shift)
    assert nan_equal(arr, expected)
