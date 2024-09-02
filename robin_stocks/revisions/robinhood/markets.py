"""Contains functions for getting market level data."""
from typing import List, Dict, Optional, Union
from functools import lru_cache

from robin_stocks.robinhood.helper import request_get, filter_data, get_output
from robin_stocks.robinhood.urls import (
    movers_sp500_url, get_100_most_popular_url, movers_top_url,
    market_category_url, markets_url, market_hours_url, currency_url
)
from robin_stocks.robinhood.stocks import get_symbol_by_url, get_quotes

def get_top_movers_sp500(direction: str, info: Optional[str] = None) -> Union[List[Dict], List[str], None]:
    """Returns a list of the top S&P500 movers up or down for the day."""
    try:
        direction = direction.lower().strip()
        if direction not in ('up', 'down'):
            raise ValueError('Error: direction must be "up" or "down"')
    except AttributeError as message:
        print(message, file=get_output())
        return None

    url = movers_sp500_url()
    payload = {'direction': direction}
    data = request_get(url, 'pagination', payload)
    return filter_data(data, info)

@lru_cache(maxsize=1)
def get_top_100(info: Optional[str] = None) -> Union[List[Dict], List[str]]:
    """Returns a list of the Top 100 stocks on Robin Hood."""
    url = get_100_most_popular_url()
    data = request_get(url, 'regular')
    instruments = filter_data(data, 'instruments')
    symbols = [get_symbol_by_url(x) for x in instruments]
    quotes = get_quotes(symbols)
    return filter_data(quotes, info)

@lru_cache(maxsize=1)
def get_top_movers(info: Optional[str] = None) -> Union[List[Dict], List[str]]:
    """Returns a list of the Top 20 movers on Robin Hood."""
    url = movers_top_url()
    data = request_get(url, 'regular')
    instruments = filter_data(data, 'instruments')
    symbols = [get_symbol_by_url(x) for x in instruments]
    quotes = get_quotes(symbols)
    return filter_data(quotes, info)

def get_all_stocks_from_market_tag(tag: str, info: Optional[str] = None) -> Union[List[Dict], List[str]]:
    """Returns all the stock quote information that matches a tag category."""
    url = market_category_url(tag)
    data = request_get(url, 'regular')
    instruments = filter_data(data, 'instruments')

    if not instruments:
        print(f'ERROR: "{tag}" is not a valid tag', file=get_output())
        return [None]

    symbols = [get_symbol_by_url(x) for x in instruments]
    quotes = get_quotes(symbols)
    return filter_data(quotes, info)

@lru_cache(maxsize=1)
def get_markets(info: Optional[str] = None) -> Union[List[Dict], List[str]]:
    """Returns a list of available markets."""
    url = markets_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

def get_market_today_hours(market: str, info: Optional[str] = None) -> Union[Dict, str]:
    """Returns the opening and closing hours of a specific market for today."""
    markets = get_markets()
    result = next((x for x in markets if x['mic'] == market), None)
    if not result:
        raise ValueError(f'Not a valid market name: {market}. Check get_markets() for a list of market information.')

    url = result['todays_hours']
    data = request_get(url, 'regular')
    return filter_data(data, info)

def get_market_next_open_hours(market: str, info: Optional[str] = None) -> Union[Dict, str]:
    """Returns the opening and closing hours for the next open trading day after today."""
    url = get_market_today_hours(market, info='next_open_hours')
    data = request_get(url, 'regular')
    return filter_data(data, info)

def get_market_next_open_hours_after_date(market: str, date: str, info: Optional[str] = None) -> Union[Dict, str]:
    """Returns the opening and closing hours for the next open trading day after a specified date."""
    url = get_market_hours(market, date, info='next_open_hours')
    data = request_get(url, 'regular')
    return filter_data(data, info)

def get_market_hours(market: str, date: str, info: Optional[str] = None) -> Union[Dict, str]:
    """Returns the opening and closing hours of a specific market on a specific date."""
    url = market_hours_url(market, date)
    data = request_get(url, 'regular')
    return filter_data(data, info)

@lru_cache(maxsize=1)
def get_currency_pairs(info: Optional[str] = None) -> Union[List[Dict], List[str]]:
    """Returns currency pairs"""
    url = currency_url()
    data = request_get(url, 'results')
    return filter_data(data, info)