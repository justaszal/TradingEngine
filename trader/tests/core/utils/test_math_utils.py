import pytest
import core.utils.math_utils as math_utils


def test_mul():
    mul_2 = math_utils.mul(2)
    assert mul_2(3) == 6
