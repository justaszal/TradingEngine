import pytest
import core.utils.strings as strings


class TestStrings():
    @pytest.mark.parametrize('input, expected', [
        ('15m', '15'),
        ('1T', '1'),
        ('a10', None),
        ('a', None),
    ])
    def test_first_number(self, input, expected):
        assert strings.first_number(input) == expected
