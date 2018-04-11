from core.errors import Error


class ExchangeNotFoundError(Error):
    msg = (
        'Exchange {exhange_name} not found. Please specify exchanges '
        'supported and verify spelling for accuracy.'
    ).strip()


class InvalidHistoryTimeframeError(Error):
    msg = (
        'CCXT timeframe {timeframe} not supported by the exchange.'
    ).strip()


class ExchangeRequestError(Error):
    msg = (
        'Request failed'
        '{e}'
    ).strip()
