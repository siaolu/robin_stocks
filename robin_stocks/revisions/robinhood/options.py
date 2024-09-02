"""Contains functions for getting information about options."""
import sys
from functools import lru_cache
from typing import Optional, List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor
from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.urls import *

def write_spinner():
    """Function to create a spinning cursor to tell user that the code is working on getting market data."""
    if get_output() == sys.stdout:
        marketString = 'Loading Market Data '
        sys.stdout.write(f"\r{marketString}{next(spinning_cursor())}")
        sys.stdout.flush()

def spinning_cursor():
    """This is a generator function to yield a character."""
    while True:
        for cursor in '|/-\\':
            yield cursor

@lru_cache(maxsize=None)
@login_required
def get_aggregate_positions(info: Optional[str] = None, account_number: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Collapses all option orders for a stock into a single dictionary."""
    try:
        url = aggregate_url(account_number=account_number)
        data = request_get(url, 'pagination')
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching aggregate positions: {e}")

@lru_cache(maxsize=None)
@login_required
def get_aggregate_open_positions(info: Optional[str] = None, account_number: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Collapses all open option positions for a stock into a single dictionary."""
    try:
        url = aggregate_url(account_number=account_number)
        payload = {'nonzero': 'True'}
        data = request_get(url, 'pagination', payload)
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching aggregate open positions: {e}")

@lru_cache(maxsize=None)
@login_required
def get_market_options(info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all options."""
    try:
        url = option_orders_url()
        data = request_get(url, 'pagination')
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching market options: {e}")

@lru_cache(maxsize=None)
@login_required
def get_all_option_positions(info: Optional[str] = None, account_number: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns all option positions ever held for the account."""
    try:
        url = option_positions_url(account_number=account_number)
        data = request_get(url, 'pagination')
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching all option positions: {e}")

@lru_cache(maxsize=None)
@login_required
def get_open_option_positions(account_number: Optional[str] = None, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns all open option positions for the account."""
    try:
        url = option_positions_url(account_number=account_number)
        payload = {'nonzero': 'True'}
        data = request_get(url, 'pagination', payload)
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching open option positions: {e}")

@lru_cache(maxsize=None)
def get_chains(symbol: str, info: Optional[str] = None) -> Union[Dict[str, Any], List[str], None]:
    """Returns the chain information of an option."""
    try:
        symbol = symbol.upper().strip()
        url = chains_url(symbol)
        data = request_get(url)
        return filter_data(data, info)
    except AttributeError as e:
        raise ValueError(f"Error processing symbol: {e}")
    except Exception as e:
        raise RuntimeError(f"Error fetching chains: {e}")

@login_required
def find_tradable_options(symbol: str, expirationDate: Optional[str] = None, strikePrice: Optional[str] = None, optionType: Optional[str] = None, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str], List[None]]:
    """Returns a list of all available options for a stock."""
    try:
        symbol = symbol.upper().strip()
        url = option_instruments_url()
        chain_id = id_for_chain(symbol)
        if not chain_id:
            raise ValueError(f"Symbol {symbol} is not valid for finding options.")

        payload = {
            'chain_id': chain_id,
            'chain_symbol': symbol,
            'state': 'active'
        }

        if expirationDate:
            payload['expiration_dates'] = expirationDate
        if strikePrice:
            payload['strike_price'] = strikePrice
        if optionType:
            payload['type'] = optionType.lower().strip()

        data = request_get(url, 'pagination', payload)
        return filter_data(data, info)
    except ValueError as e:
        raise ValueError(f"Error finding tradable options: {e}")
    except Exception as e:
        raise RuntimeError(f"Error fetching tradable options: {e}")

@login_required
def find_options_by_expiration(inputSymbols: Union[str, List[str]], expirationDate: str, optionType: Optional[str] = None, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the option orders that match the search parameters"""
    symbols = inputs_to_set(inputSymbols)
    data = []

    def process_symbol(symbol):
        try:
            allOptions = find_tradable_options(symbol, expirationDate, None, optionType, None)
            filteredOptions = [item for item in allOptions if item.get("expiration_date") == expirationDate]

            for item in filteredOptions:
                marketData = get_option_market_data_by_id(item['id'])
                if marketData:
                    item.update(marketData[0])
                write_spinner()

            return filteredOptions
        except Exception as e:
            raise RuntimeError(f"Error processing symbol {symbol}: {e}")

    try:
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_symbol, symbols))

        data = [item for sublist in results for item in sublist]
        return filter_data(data, info)
    except Exception as e:
        raise RuntimeError(f"Error finding options by expiration: {e}")

def get_option_historicals(symbol: str, expirationDate: str, strikePrice: str, optionType: Optional[str] = None, interval: str = 'hour', span: str = 'week', bounds: str = 'regular', info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str], List[None]]:
    """Returns the data that is used to make the graphs."""
    try:
        symbol = symbol.upper().strip()
        optionType = optionType.lower().strip() if optionType else None
    except AttributeError as e:
        raise ValueError(f"Error processing input: {e}")

    interval_check = ['5minute', '10minute', 'hour', 'day', 'week']
    span_check = ['day', 'week', 'year', '5year']
    bounds_check = ['extended', 'regular', 'trading']

    if interval not in interval_check:
        raise ValueError('ERROR: Interval must be "5minute","10minute","hour","day",or "week"')
    if span not in span_check:
        raise ValueError('ERROR: Span must be "day", "week", "year", or "5year"')
    if bounds not in bounds_check:
        raise ValueError('ERROR: Bounds must be "extended","regular",or "trading"')

    optionID = id_for_option(symbol, expirationDate, strikePrice, optionType)

    try:
        url = option_historicals_url(optionID)
        payload = {'span': span, 'interval': interval, 'bounds': bounds}
        data = request_get(url, 'regular', payload)

        if data is None or data == [None]:
            return [None]

        histData = [dict(subitem, symbol=symbol) for subitem in data['data_points']]
        return filter_data(histData, info)
    except Exception as e:
        raise RuntimeError(f"Error fetching option historicals: {e}")
