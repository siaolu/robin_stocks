"""Contains functions for getting information related to the user account."""
import os
from uuid import uuid4
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.profiles import *
from robin_stocks.robinhood.stocks import *
from robin_stocks.robinhood.urls import *

@login_required
@lru_cache(maxsize=1)
def load_phoenix_account(info=None):
    """Returns unified information about your account."""
    url = phoenix_url()
    data = request_get(url, 'regular')
    return filter_data(data, info)

@login_required
def get_historical_portfolio(interval=None, span='week', bounds='regular', info=None):
    """Gets historical portfolio data."""
    interval_check = ['5minute', '10minute', 'hour', 'day', 'week']
    span_check = ['day', 'week', 'month', '3month', 'year', '5year', 'all']
    bounds_check = ['extended', 'regular', 'trading']

    if interval not in interval_check:
        if interval is None and (bounds != 'regular' and span != 'all'):
            print('ERROR: Interval must be None for "all" span "regular" bounds', file=get_output())
            return [None]
        print('ERROR: Invalid interval', file=get_output())
        return [None]
    if span not in span_check:
        print('ERROR: Invalid span', file=get_output())
        return [None]
    if bounds not in bounds_check:
        print('ERROR: Invalid bounds', file=get_output())
        return [None]
    if (bounds in ['extended', 'trading']) and span != 'day':
        print('ERROR: extended and trading bounds can only be used with a span of "day"', file=get_output())
        return [None]

    account = load_account_profile(info='account_number')
    url = portfolis_historicals_url(account)
    payload = {'interval': interval, 'span': span, 'bounds': bounds}
    data = request_get(url, 'regular', payload)
    return filter_data(data, info)

@login_required
@lru_cache(maxsize=1)
def get_all_positions(info=None):
    """Returns a list containing every position ever traded."""
    url = positions_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@login_required
def get_open_stock_positions(account_number=None, info=None):
    """Returns a list of stocks that are currently held."""
    url = positions_url(account_number=account_number)
    payload = {'nonzero': 'true'}
    data = request_get(url, 'pagination', payload)
    return filter_data(data, info)

@login_required
@lru_cache(maxsize=1)
def get_dividends(info=None):
    """Returns a list of dividend transactions."""
    url = dividends_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@login_required
def get_total_dividends():
    """Returns the total amount of dividends paid to the account."""
    dividends = get_dividends()
    return sum(float(item['amount']) for item in dividends if item['state'] in ['paid', 'reinvested'])

@login_required
def get_dividends_by_instrument(instrument, dividend_data):
    """Returns dividend data for a specific instrument."""
    data = [x for x in dividend_data if x['instrument'] == instrument]
    if not data:
        return None
    
    dividend = float(data[0]['rate'])
    total_dividends = float(data[0]['amount'])
    total_amount_paid = sum(float(d['amount']) for d in data)

    return {
        'dividend_rate': f"{dividend:.2f}",
        'total_dividend': f"{total_dividends:.2f}",
        'amount_paid_to_date': f"{total_amount_paid:.2f}"
    }

# ... [other functions remain largely unchanged] ...

@login_required
def build_holdings(with_dividends=False):
    """Builds a dictionary of important information regarding the stocks and positions owned by the user."""
    positions_data = get_open_stock_positions()
    portfolios_data = load_portfolio_profile()
    accounts_data = load_account_profile()
    dividend_data = get_dividends() if with_dividends else None

    if not all([positions_data, portfolios_data, accounts_data]):
        return {}

    total_equity = max(float(portfolios_data['equity']), float(portfolios_data['extended_hours_equity'] or 0))
    cash = float(accounts_data['cash']) + float(accounts_data['uncleared_deposits'])

    def process_position(item):
        if not item:
            return None
        
        instrument_data = get_instrument_by_url(item['instrument'])
        symbol = instrument_data['symbol']
        fundamental_data = get_fundamentals(symbol)[0]
        price = float(get_latest_price(symbol)[0])
        quantity = float(item['quantity'])
        average_buy_price = float(item['average_buy_price'])
        
        equity = quantity * price
        equity_change = equity - (quantity * average_buy_price)
        percentage = equity * 100 / (total_equity - cash)
        percent_change = ((price - average_buy_price) * 100 / average_buy_price) if average_buy_price != 0 else 0
        
        holding = {
            'price': str(price),
            'quantity': str(quantity),
            'average_buy_price': item['average_buy_price'],
            'equity': f"{equity:.2f}",
            'percent_change': f"{percent_change:.2f}",
            'equity_change': f"{equity_change:.2f}",
            'type': instrument_data['type'],
            'name': get_name_by_symbol(symbol),
            'id': instrument_data['id'],
            'pe_ratio': fundamental_data['pe_ratio'],
            'percentage': f"{percentage:.2f}"
        }

        if with_dividends:
            holding.update(get_dividends_by_instrument(item['instrument'], dividend_data) or {})

        return symbol, holding

    with ThreadPoolExecutor() as executor:
        holdings = dict(filter(None, executor.map(process_position, positions_data)))

    return holdings

@login_required
@lru_cache(maxsize=1)
def build_user_profile(account_number=None):
    """Builds a dictionary of important information regarding the user account."""
    portfolios_data = load_portfolio_profile(account_number=account_number)
    accounts_data = load_account_profile(account_number=account_number)

    user = {}
    if portfolios_data:
        user['equity'] = portfolios_data['equity']
        user['extended_hours_equity'] = portfolios_data['extended_hours_equity']

    if accounts_data:
        user['cash'] = f"{float(accounts_data['portfolio_cash']):.2f}"

    user['dividend_total'] = get_total_dividends()

    return user