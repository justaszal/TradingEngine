class Error(Exception):
    msg = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return self.msg.format(**self.kwargs)

    __unicode__ = __str__
    __repr__ = __str__


class PriceHandlerNotFoundError(Error):
    msg = (
        'Price handler {price_handler} could not be find in core.price_handler'
        'directory and {price_handler} is not of type PriceHandler.'
    )


class TradingSessionTypeError(Error):
    msg = (
        'Trading session type can only be backtest or live however'
        '{session_type} was passed.'
    )
