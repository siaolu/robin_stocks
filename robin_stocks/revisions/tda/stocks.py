# stocks.py revision
# Rev 1.3 (experimental)
# Date: 2024-09-01
# Revised by: dasConnOps

from robin_stocks.tda.helper import format_inputs, login_required, request_get
from robin_stocks.tda.urls import URLS
from functools import lru_cache
import asyncio
import aiohttp

@lru_cache(maxsize=128)
@login_required
@format_inputs
async def get_quote_async(ticker, session):
    """Gets quote information for a single stock asynchronously."""
    url = URLS.quote(ticker)
    async with session.get(url) as response:
        return await response.json()

@login_required
@format_inputs
async def get_quotes_async(tickers):
    """Gets quote information for multiple stocks asynchronously."""
    url = URLS.quotes()
    async with aiohttp.ClientSession() as session:
        tasks = [get_quote_async(ticker, session) for ticker in tickers.split(',')]
        return await asyncio.gather(*tasks)

@login_required
@format_inputs
def get_price_history(ticker, period_type, frequency_type, frequency,
                      period=None, start_date=None, end_date=None, need_extended_hours_data=True):
    """Gets the price history of a stock."""
    if (start_date or end_date) and period:
        raise ValueError("If start_date and end_date are provided, period should not be provided.")
    
    url = URLS.price_history(ticker)
    payload = {
        "periodType": period_type,
        "frequencyType": frequency_type,
        "frequency": frequency,
        "needExtendedHoursData": need_extended_hours_data
    }
    if period:
        payload["period"] = period
    if start_date:
        payload["startDate"] = start_date
    if end_date:
        payload["endDate"] = end_date
    
    return request_get(url, payload)

@lru_cache(maxsize=128)
@login_required
@format_inputs
def search_instruments(ticker_string, projection):
    """Gets a list of all the instruments data for tickers that match a search string."""
    url = URLS.instruments()
    payload = {
        "symbol": ticker_string,
        "projection": projection
    }
    return request_get(url, payload)

@lru_cache(maxsize=128)
@login_required
@format_inputs
def get_instrument(cusip):
    """Gets instrument data for a specific stock."""
    url = URLS.instrument(cusip)
    return request_get(url)

@login_required
@format_inputs
def get_option_chains(ticker, **kwargs):
    """Gets option chain data for a specific stock."""
    url = URLS.option_chains()
    payload = {
        "symbol": ticker,
        "contractType": kwargs.get('contract_type', "ALL"),
        "strikeCount": kwargs.get('strike_count', "10"),
        "includeQuotes": kwargs.get('include_quotes', "FALSE"),
        "strategy": kwargs.get('strategy', "SINGLE"),
        "range": kwargs.get('range_value', "ALL"),
        "expMonth": kwargs.get('exp_month', "ALL"),
        "optionType": kwargs.get('option_type', "ALL")
    }
    
    optional_params = ['interval', 'strike', 'fromDate', 'toDate', 'volatility', 'underlyingPrice', 'interestRate', 'daysToExpiration']
    payload.update({k: v for k, v in kwargs.items() if k in optional_params and v is not None})
    
    return request_get(url, payload)