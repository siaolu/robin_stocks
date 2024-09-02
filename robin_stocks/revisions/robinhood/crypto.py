"""Contains functions to get information about crypto-currencies."""
from functools import lru_cache
from robin_stocks.robinhood.helper import request_get, login_required, inputs_to_set, filter_data, get_output
from robin_stocks.robinhood.urls import (
    crypto_account_url, crypto_holdings_url, crypto_currency_pairs_url,
    crypto_quote_url, crypto_historical_url
)

@login_required
@lru_cache(maxsize=1)
def load_crypto_profile(info=None):
    """Gets the information associated with the crypto account."""
    url = crypto_account_url()
    data = request_get(url, 'indexzero')
    return filter_data(data, info)

@login_required
def get_crypto_positions(info=None):
    """Returns crypto positions for the account."""
    url = crypto_holdings_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@lru_cache(maxsize=100)
def get_crypto_currency_pairs(info=None):
    """Gets a list of all the crypto currencies that you can trade."""
    url = crypto_currency_pairs_url()
    data = request_get(url, 'results')
    return filter_data(data, info)

@lru_cache(maxsize=100)
def get_crypto_info(symbol, info=None):
    """Gets information about a crypto currency."""
    data = get_crypto_currency_pairs()
    data = [x for x in data if x['asset_currency']['code'] == symbol]
    return filter_data(data[0] if data else None, info)

SYMBOL_TO_ID_CACHE = {}
def get_crypto_id(symbol):
    """Gets the Robinhood ID of the given cryptocurrency used to make trades."""
    if symbol not in SYMBOL_TO_ID_CACHE:
        SYMBOL_TO_ID_CACHE[symbol] = get_crypto_info(symbol, 'id')
    return SYMBOL_TO_ID_CACHE[symbol]

@login_required
def get_crypto_quote(symbol, info=None):
    """Gets information about a crypto including low price, high price, and open price"""
    id = get_crypto_id(symbol)
    if not id:
        return None
    url = crypto_quote_url(id)
    data = request_get(url)
    return filter_data(data, info)

@login_required
def get_crypto_quote_from_id(id, info=None):
    """Gets information about a crypto including low price, high price, and open price. Uses the id instead of crypto ticker."""
    url = crypto_quote_url(id)
    data = request_get(url)
    return filter_data(data, info)

@login_required
def get_crypto_historicals(symbol, interval='hour', span='week', bounds='24_7', info=None):
    """Gets historical information about a crypto including open price, close price, high price, and low price."""
    interval_check = {'15second', '5minute', '10minute', 'hour', 'day', 'week'}
    span_check = {'hour', 'day', 'week', 'month', '3month', 'year', '5year'}
    bounds_check = {'24_7', 'extended', 'regular', 'trading'}

    if interval not in interval_check:
        raise ValueError("Invalid interval. Must be one of: " + ", ".join(interval_check))
    if span not in span_check:
        raise ValueError("Invalid span. Must be one of: " + ", ".join(span_check))
    if bounds not in bounds_check:
        raise ValueError("Invalid bounds. Must be one of: " + ", ".join(bounds_check))
    if bounds in {'extended', 'trading'} and span != 'day':
        raise ValueError("Extended and trading bounds can only be used with a span of 'day'")

    symbol = inputs_to_set(symbol)
    id = get_crypto_id(symbol.pop())
    if not id:
        return None

    url = crypto_historical_url(id)
    payload = {'interval': interval, 'span': span, 'bounds': bounds}
    data = request_get(url, 'regular', payload)

    if not data or 'data_points' not in data:
        return None

    hist_data = [dict(item, symbol=data['symbol']) for item in data['data_points']]
    return filter_data(hist_data, info)