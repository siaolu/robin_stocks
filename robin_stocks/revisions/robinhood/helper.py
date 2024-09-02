"""Contains decorator functions and utility functions for interacting with global data."""
from functools import wraps, lru_cache
from typing import Any, List, Dict, Union, Callable
import requests
from robin_stocks.robinhood.globals import robinhood_globals as rg

def login_required(func: Callable) -> Callable:
    """A decorator for indicating which methods require the user to be logged in."""
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        if not rg.logged_in:
            raise Exception(f'{func.__name__} can only be called when logged in')
        return func(*args, **kwargs)
    return login_wrapper

def convert_none_to_string(func: Callable) -> Callable:
    """A decorator for converting a None Type into a blank string"""
    @wraps(func)
    def string_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return "" if result is None else result
    return string_wrapper

@lru_cache(maxsize=128)
def id_for_stock(symbol: str) -> Union[str, None]:
    """Takes a stock ticker and returns the instrument id associated with the stock."""
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        print(message, file=rg.get_output())
        return None

    url = 'https://api.robinhood.com/instruments/'
    payload = {'symbol': symbol}
    data = request_get(url, 'indexzero', payload)
    return filter_data(data, 'id')

@lru_cache(maxsize=128)
def id_for_chain(symbol: str) -> Union[str, None]:
    """Takes a stock ticker and returns the chain id associated with a stock's option."""
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        print(message, file=rg.get_output())
        return None

    url = 'https://api.robinhood.com/instruments/'
    payload = {'symbol': symbol}
    data = request_get(url, 'indexzero', payload)
    return data['tradable_chain_id'] if data else None

@lru_cache(maxsize=128)
def id_for_group(symbol: str) -> Union[str, None]:
    """Takes a stock ticker and returns the id associated with the group."""
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        print(message, file=rg.get_output())
        return None

    url = f'https://api.robinhood.com/options/chains/{id_for_chain(symbol)}/'
    data = request_get(url)
    return data['underlying_instruments'][0]['id'] if data else None

@lru_cache(maxsize=128)
def id_for_option(symbol: str, expirationDate: str, strike: str, optionType: str) -> Union[str, None]:
    """Returns the id associated with a specific option order."""
    symbol = symbol.upper()
    chain_id = id_for_chain(symbol)
    payload = {
        'chain_id': chain_id,
        'expiration_dates': expirationDate,
        'strike_price': strike,
        'type': optionType,
        'state': 'active'
    }
    url = 'https://api.robinhood.com/options/instruments/'
    data = request_get(url, 'pagination', payload)

    listOfOptions = [item for item in data if item["expiration_date"] == expirationDate]
    if not listOfOptions:
        print('Getting the option ID failed. Perhaps the expiration date is wrong format, or the strike price is wrong.', file=rg.get_output())
        return None

    return listOfOptions[0]['id']

def round_price(price: float) -> float:
    """Takes a price and rounds it to an appropriate decimal place that Robinhood will accept."""
    price = float(price)
    if price <= 1e-2:
        return round(price, 6)
    elif price < 1e0:
        return round(price, 4)
    else:
        return round(price, 2)

def filter_data(data: Union[Dict, List], info: str = None) -> Any:
    """Takes the data and extracts the value for the keyword that matches info."""
    if data is None:
        return data
    elif data == [None]:
        return []
    
    if isinstance(data, list):
        if not data:
            return []
        compareDict = data[0]
    elif isinstance(data, dict):
        compareDict = data
    else:
        return data

    if info is not None:
        if info in compareDict:
            return [x[info] for x in data] if isinstance(data, list) else data[info]
        else:
            print(f"Error: '{info}' is not a key in the dictionary.", file=rg.get_output())
            return [] if isinstance(data, list) else None
    else:
        return data

def inputs_to_set(inputSymbols: Union[str, List, Dict, tuple]) -> List[str]:
    """Takes in the parameters passed to *args and puts them in a set and a list."""
    symbols_set = set()
    symbols_list = []

    def add_symbol(symbol: str):
        symbol = symbol.upper().strip()
        if symbol not in symbols_set:
            symbols_set.add(symbol)
            symbols_list.append(symbol)

    if isinstance(inputSymbols, str):
        add_symbol(inputSymbols)
    elif isinstance(inputSymbols, (list, tuple, set)):
        for item in inputSymbols:
            if isinstance(item, str):
                add_symbol(item)

    return symbols_list

def request_document(url: str, payload: Dict = None) -> requests.Response:
    """Using a document url, makes a get request and returns the session data."""
    try:
        res = rg.session.get(url, params=payload)
        res.raise_for_status()
        return res
    except requests.exceptions.HTTPError as message:
        print(message, file=rg.get_output())
        return None

def request_get(url: str, dataType: str = 'regular', payload: Dict = None, jsonify_data: bool = True) -> Any:
    """For a given url and payload, makes a get request and returns the data."""
    if dataType in ('results', 'pagination'):
        data = [None]
    else:
        data = None
    
    try:
        res = rg.session.get(url, params=payload)
        res.raise_for_status()
        if jsonify_data:
            data = res.json()
        else:
            return res
    except (requests.exceptions.HTTPError, AttributeError) as message:
        print(message, file=rg.get_output())
        return data

    if dataType == 'results':
        data = data.get('results', [None])
    elif dataType == 'pagination':
        data = data.get('results', [])
        while 'next' in data and data['next']:
            try:
                res = rg.session.get(data['next'])
                res.raise_for_status()
                next_data = res.json()
                data.extend(next_data.get('results', []))
            except:
                print('Additional pages exist but could not be loaded.', file=rg.get_output())
                break
    elif dataType == 'indexzero':
        data = data.get('results', [{}])[0]

    return data

def request_post(url: str, payload: Dict = None, timeout: int = 16, json: bool = False, jsonify_data: bool = True) -> Any:
    """For a given url and payload, makes a post request and returns the response."""
    try:
        if json:
            rg.session.headers['Content-Type'] = 'application/json'
            res = rg.session.post(url, json=payload, timeout=timeout)
        else:
            res = rg.session.post(url, data=payload, timeout=timeout)
        
        res.raise_for_status()
        data = res.json() if jsonify_data else res
    except Exception as message:
        print(f"Error in request_post: {message}", file=rg.get_output())
        data = None
    finally:
        rg.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
    
    return data

def request_delete(url: str) -> requests.Response:
    """For a given url, makes a delete request and returns the response."""
    try:
        res = rg.session.delete(url)
        res.raise_for_status()
        return res
    except Exception as message:
        print(f"Error in request_delete: {message}", file=rg.get_output())
        return None

def update_session(key: str, value: str):
    """Updates the session header used by the requests library."""
    rg.session.headers[key] = value

# Error message functions
def error_argument_not_key_in_dictionary(keyword: str) -> str:
    return f'Error: The keyword "{keyword}" is not a key in the dictionary.'

def error_ticker_does_not_exist(ticker: str) -> str:
    return f'Warning: "{ticker}" is not a valid stock ticker. It is being ignored'

def error_must_be_nonzero(keyword: str) -> str:
    return f'Error: The input parameter "{keyword}" must be an integer larger than zero and non-negative'