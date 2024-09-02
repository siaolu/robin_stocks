"""Contains functions for handling stock-related data."""
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Union

from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.urls import *

def get_quotes(inputSymbols: Union[str, List[str]], info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches price-related information for one or more stock tickers.

    :param inputSymbols: Single stock ticker or a list of stock tickers.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing key/value pairs for each ticker, or a list of specific values if `info` is provided.
    """
    symbols = inputs_to_set(inputSymbols)
    url = quotes_url()
    payload = {'symbols': ','.join(symbols)}
    data = request_get(url, 'results', payload)

    if not data:
        raise ValueError("Failed to fetch quotes for symbols: {}".format(','.join(symbols)))

    data = [item for item in data if item is not None]

    return filter_data(data, info)


def get_fundamentals(inputSymbols: Union[str, List[str]], info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches fundamental data for one or more stock tickers, such as sector, description, and market cap.

    :param inputSymbols: Single stock ticker or a list of stock tickers.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing key/value pairs for each ticker, or a list of specific values if `info` is provided.
    """
    symbols = inputs_to_set(inputSymbols)
    url = fundamentals_url()
    payload = {'symbols': ','.join(symbols)}
    data = request_get(url, 'results', payload)

    if not data:
        raise ValueError("Failed to fetch fundamentals for symbols: {}".format(','.join(symbols)))

    for count, item in enumerate(data):
        if item:
            item['symbol'] = symbols[count]

    return filter_data([item for item in data if item is not None], info)


def get_instruments_by_symbols(inputSymbols: Union[str, List[str]], info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches market data related to one or more stock tickers, such as ticker name and listing date.

    :param inputSymbols: Single stock ticker or a list of stock tickers.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing key/value pairs for each ticker, or a list of specific values if `info` is provided.
    """
    symbols = inputs_to_set(inputSymbols)
    url = instruments_url()
    results = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(request_get, url, 'indexzero', {'symbol': symbol}) for symbol in symbols]
        for future in futures:
            item_data = future.result()
            if item_data:
                results.append(item_data)
            else:
                raise ValueError(f"Ticker {symbol} does not exist.")

    return filter_data(results, info)


def get_latest_price(inputSymbols: Union[str, List[str]], priceType: Optional[str] = None, includeExtendedHours: bool = True) -> List[str]:
    """Fetches the latest price for one or more stock tickers.

    :param inputSymbols: Single stock ticker or a list of stock tickers.
    :param priceType: Can either be 'ask_price' or 'bid_price'. If set, `includeExtendedHours` is ignored.
    :param includeExtendedHours: Whether to include extended hours prices.
    :returns: A list of prices as strings.
    """
    symbols = inputs_to_set(inputSymbols)
    quotes = get_quotes(symbols)
    prices = []

    for item in quotes:
        if item:
            if priceType == 'ask_price':
                prices.append(item.get('ask_price'))
            elif priceType == 'bid_price':
                prices.append(item.get('bid_price'))
            else:
                if priceType:
                    raise ValueError(f"Invalid priceType '{priceType}'. Must be 'ask_price' or 'bid_price'.")
                prices.append(item['last_extended_hours_trade_price'] if includeExtendedHours else item['last_trade_price'])
        else:
            prices.append(None)

    return prices


@lru_cache(maxsize=None)
@convert_none_to_string
def get_name_by_symbol(symbol: str) -> Optional[str]:
    """Fetches the name of a stock from its ticker symbol.

    :param symbol: The stock ticker.
    :returns: The name of the stock, or None if not found.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    url = instruments_url()
    data = request_get(url, 'indexzero', {'symbol': symbol})

    if not data:
        raise ValueError(f"Could not find instrument for symbol: {symbol}")

    return data.get('simple_name') or data.get('name')


@lru_cache(maxsize=None)
@convert_none_to_string
def get_symbol_by_url(url: str) -> Optional[str]:
    """Fetches the ticker symbol of a stock from its instrument URL.

    :param url: The instrument URL.
    :returns: The ticker symbol, or None if not found.
    """
    data = request_get(url)

    if not data:
        raise ValueError(f"Could not find instrument for URL: {url}")

    return data.get('symbol')


def get_ratings(symbol: str, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Fetches ratings data for a stock, including buy, hold, and sell ratings.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A dictionary of ratings data, or a specific value if `info` is provided.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    url = ratings_url(symbol)
    data = request_get(url)

    if not data or not data.get('ratings'):
        raise ValueError(f"No ratings data found for symbol: {symbol}")

    return filter_data(data, info)


def get_news(symbol: str, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches news stories related to a stock ticker.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing news data, or a list of specific values if `info` is provided.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    url = news_url(symbol)
    data = request_get(url, 'results')

    if not data:
        raise ValueError(f"No news found for symbol: {symbol}")

    return filter_data(data, info)


def get_stock_historicals(inputSymbols: Union[str, List[str]], interval: str = 'hour', span: str = 'week', bounds: str = 'regular', info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches historical data for one or more stock tickers.

    :param inputSymbols: Single stock ticker or a list of stock tickers.
    :param interval: Interval to retrieve data for. Options are '5minute', '10minute', 'hour', 'day', 'week'.
    :param span: The range of data. Options are 'day', 'week', 'month', '3month', 'year', '5year'.
    :param bounds: Whether to include extended trading hours. Options are 'extended', 'regular', 'trading'.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing historical data, or a list of specific values if `info` is provided.
    """
    interval_check = ['5minute', '10minute', 'hour', 'day', 'week']
    span_check = ['day', 'week', 'month', '3month', 'year', '5year']
    bounds_check = ['extended', 'regular', 'trading']

    if interval not in interval_check:
        raise ValueError(f"Invalid interval: {interval}. Must be one of {interval_check}.")
    if span not in span_check:
        raise ValueError(f"Invalid span: {span}. Must be one of {span_check}.")
    if bounds not in bounds_check:
        raise ValueError(f"Invalid bounds: {bounds}. Must be one of {bounds_check}.")
    if (bounds == 'extended' or bounds == 'trading') and span != 'day':
        raise ValueError(f"'extended' and 'trading' bounds can only be used with a span of 'day'.")

    symbols = inputs_to_set(inputSymbols)
    url = historicals_url()
    payload = {'symbols': ','.join(symbols), 'interval': interval, 'span': span, 'bounds': bounds}
    data = request_get(url, 'results', payload)

    if not data:
        raise ValueError(f"Failed to fetch historicals for symbols: {','.join(symbols)}")

    histData = []
    for count, item in enumerate(data):
        if not item['historicals']:
            raise ValueError(f"No historicals found for symbol: {symbols[count]}")
        stockSymbol = item['symbol']
        for subitem in item['historicals']:
            subitem['symbol'] = stockSymbol
            histData.append(subitem)

    return filter_data(histData, info)


def get_earnings(symbol: str, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches earnings data for a stock ticker, including EPS and financial reports.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing earnings data, or a list of specific values if `info` is provided.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    url = earnings_url()
    payload = {'symbol': symbol}
    data = request_get(url, 'results', payload)

    if not data:
        raise ValueError(f"No earnings data found for symbol: {symbol}")

    return filter_data(data, info)


def get_splits(symbol: str, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches stock split information for a stock ticker, including date, divisor, and multiplier.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing split data, or a list of specific values if `info` is provided.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    url = splits_url(symbol)
    data = request_get(url, 'results')

    if not data:
        raise ValueError(f"No split data found for symbol: {symbol}")

    return filter_data(data, info)


def get_events(symbol: str, info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Fetches events related to a stock ticker, such as stock splits or dividends.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A list of dictionaries containing event data, or a list of specific values if `info` is provided.
    """
    try:
        symbol = symbol.upper().strip()
    except AttributeError:
        raise ValueError(f"Invalid symbol: {symbol}")

    payload = {'equity_instrument_id': id_for_stock(symbol)}
    url = events_url()
    data = request_get(url, 'results', payload)

    if not data:
        raise ValueError(f"No events data found for symbol: {symbol}")

    return filter_data(data, info)


def find_instrument_data(query: str) -> List[Dict[str, Any]]:
    """Searches for stocks that match a query keyword and returns their instrument data.

    :param query: The keyword to search for.
    :returns: A list of dictionaries containing the instrument data for each stock that matches the query.
    """
    url = instruments_url()
    payload = {'query': query}
    data = request_get(url, 'pagination', payload)

    if not data:
        raise ValueError(f"No results found for the query: {query}")

    return data


def get_stock_quote_by_id(stock_id: str, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Fetches stock quote information by its Robinhood stock ID.

    :param stock_id: The Robinhood stock ID.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A dictionary of stock quote data, or a specific value if `info` is provided.
    """
    url = marketdata_quotes_url(stock_id)
    data = request_get(url)

    if not data:
        raise ValueError(f"No quote data found for stock ID: {stock_id}")

    return filter_data(data, info)


def get_stock_quote_by_symbol(symbol: str, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Fetches stock quote information by its ticker symbol.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A dictionary of stock quote data, or a specific value if `info` is provided.
    """
    stock_id = id_for_stock(symbol)
    return get_stock_quote_by_id(stock_id, info)


def get_pricebook_by_id(stock_id: str, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Fetches Level II market data (price book) by Robinhood stock ID.

    :param stock_id: The Robinhood stock ID.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A dictionary containing price book data, or a specific value if `info` is provided.
    """
    url = marketdata_pricebook_url(stock_id)
    data = request_get(url)

    if not data:
        raise ValueError(f"No price book data found for stock ID: {stock_id}")

    return filter_data(data, info)


def get_pricebook_by_symbol(symbol: str, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Fetches Level II market data (price book) by stock ticker symbol.

    :param symbol: The stock ticker.
    :param info: Optional parameter to filter the results by a specific key.
    :returns: A dictionary containing price book data, or a specific value if `info` is provided.
    """
    stock_id = id_for_stock(symbol)
    return get_pricebook_by_id(stock_id, info)



