import pytest
import datetime


@pytest.fixture(scope='session')
def two_sequential_days(request):
    """Return array of days of 2018 year


    Args:
        request (Object): which day to return

    Returns:
        Returns two days or one depending whether parameter is passed
        Array: [start_dt, end_dt]
    """
    dates = [
        datetime.datetime(2018, 1, 1),
        datetime.datetime(2018, 1, 2)
    ]

    return ([dates[request.param]] if
            hasattr(request, 'param') and
            request.param is not None else
            dates)
