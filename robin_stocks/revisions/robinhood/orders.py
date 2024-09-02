"""Contains all functions for placing orders for stocks, options, and crypto."""
from uuid import uuid4
from typing import Optional, List, Dict, Any
from robin_stocks.robinhood.crypto import *
from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.profiles import *
from robin_stocks.robinhood.stocks import *
from robin_stocks.robinhood.urls import *

@login_required
def get_all_stock_orders(info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the orders that have been processed for the account."""
    url = orders_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@login_required
def get_all_option_orders(info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the option orders that have been processed for the account."""
    url = option_orders_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@login_required
def get_all_crypto_orders(info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the crypto orders that have been processed for the account."""
    url = crypto_orders_url()
    data = request_get(url, 'pagination')
    return filter_data(data, info)

@login_required
def get_all_open_stock_orders(info: Optional[str] = None, account_number: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the orders that are currently open."""
    url = orders_url(account_number=account_number)
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    return filter_data(open_orders, info)

@login_required
def get_all_open_option_orders(info: Optional[str] = None, account_number: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the orders that are currently open."""
    url = option_orders_url(account_number=account_number)
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    return filter_data(open_orders, info)

@login_required
def get_all_open_crypto_orders(info: Optional[str] = None) -> Union[List[Dict[str, Any]], List[str]]:
    """Returns a list of all the crypto orders that are currently open."""
    url = crypto_orders_url()
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    return filter_data(open_orders, info)

@login_required
def get_stock_order_info(orderID: str) -> Dict[str, Any]:
    """Returns the information for a single order."""
    url = orders_url(orderID)
    data = request_get(url)
    if data is None:
        raise ValueError(f"No order found with ID: {orderID}")
    return data

@login_required
def get_option_order_info(order_id: str) -> Dict[str, Any]:
    """Returns the information for a single option order."""
    url = option_orders_url(order_id)
    data = request_get(url)
    if data is None:
        raise ValueError(f"No option order found with ID: {order_id}")
    return data

@login_required
def get_crypto_order_info(order_id: str) -> Dict[str, Any]:
    """Returns the information for a single crypto order."""
    url = crypto_orders_url(order_id)
    data = request_get(url)
    if data is None:
        raise ValueError(f"No crypto order found with ID: {order_id}")
    return data

@login_required
def find_stock_orders(**arguments) -> Union[List[Dict[str, Any]], None]:
    """Returns a list of orders that match the keyword parameters."""
    url = orders_url()
    data = request_get(url, 'pagination')

    if not arguments:
        return data

    for key in ['quantity', 'cumulative_quantity']:
        for item in data:
            item[key] = str(float(item[key]))

    if 'symbol' in arguments:
        arguments['instrument'] = get_instruments_by_symbols(arguments['symbol'], info='url')[0]
        del arguments['symbol']

    if 'quantity' in arguments:
        arguments['quantity'] = str(arguments['quantity'])

    filtered_orders = []
    for item in data:
        if all(item.get(key) == value for key, value in arguments.items()):
            filtered_orders.append(item)

    if not filtered_orders:
        raise ValueError("No matching orders found.")
    
    return filtered_orders

@login_required
def cancel_stock_order(orderID: str) -> Dict[str, Any]:
    """Cancels a specific order."""
    url = cancel_url(orderID)
    data = request_post(url)
    if data:
        return data
    else:
        raise ValueError(f"Failed to cancel order with ID: {orderID}")

@login_required
def cancel_option_order(orderID: str) -> Dict[str, Any]:
    """Cancels a specific option order."""
    url = option_cancel_url(orderID)
    data = request_post(url)
    if data:
        return data
    else:
        raise ValueError(f"Failed to cancel option order with ID: {orderID}")

@login_required
def cancel_crypto_order(orderID: str) -> Dict[str, Any]:
    """Cancels a specific crypto order."""
    url = crypto_cancel_url(orderID)
    data = request_post(url)
    if data:
        return data
    else:
        raise ValueError(f"Failed to cancel crypto order with ID: {orderID}")

@login_required
def cancel_all_stock_orders() -> List[Dict[str, Any]]:
    """Cancels all stock orders."""
    url = orders_url()
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    
    for item in open_orders:
        request_post(item['cancel_url'])

    if open_orders:
        return open_orders
    else:
        raise ValueError("No open stock orders to cancel.")

@login_required
def cancel_all_option_orders() -> List[Dict[str, Any]]:
    """Cancels all option orders."""
    url = option_orders_url()
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    
    for item in open_orders:
        request_post(item['cancel_url'])

    if open_orders:
        return open_orders
    else:
        raise ValueError("No open option orders to cancel.")

@login_required
def cancel_all_crypto_orders() -> List[Dict[str, Any]]:
    """Cancels all crypto orders."""
    url = crypto_orders_url()
    data = request_get(url, 'pagination')
    open_orders = [item for item in data if item.get('cancel_url')]
    
    for item in open_orders:
        request_post(item['cancel_url'])

    if open_orders:
        return open_orders
    else:
        raise ValueError("No open crypto orders to cancel.")

@login_required
def order(symbol: str, quantity: float, side: str, limitPrice: Optional[float] = None, stopPrice: Optional[float] = None, account_number: Optional[str] = None, timeInForce: str = 'gtc', extendedHours: bool = False, jsonify: bool = True, market_hours: str = 'regular_hours') -> Dict[str, Any]:
    """A generic order function."""
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        raise ValueError(f"Invalid symbol: {symbol}") from message

    orderType = "market"
    trigger = "immediate"
    priceType = "ask_price" if side == "buy" else "bid_price"

    if limitPrice and stopPrice:
        price = round_price(limitPrice)
        stopPrice = round_price(stopPrice)
        orderType = "limit"
        trigger = "stop"
    elif limitPrice:
        price = round_price(limitPrice)
        orderType = "limit"
    elif stopPrice:
        stopPrice = round_price(stopPrice)
        price = stopPrice if side == "buy" else None
        trigger = "stop"
    else:
        price = round_price(next(iter(get_latest_price(symbol, priceType, extendedHours)), 0.00))
        
    payload = {
        'account': load_account_profile(account_number=account_number, info='url'),
        'instrument': get_instruments_by_symbols(symbol, info='url')[0],
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'ref_id': str(uuid4()),
        'type': orderType,
        'stop_price': stopPrice,
        'time_in_force': timeInForce,
        'trigger': trigger,
        'side': side,
        'market_hours': market_hours,
        'extended_hours': extendedHours
    }

    url = orders_url()
    data = request_post(url, payload, jsonify_data=jsonify)
    
    if data:
        return data
    else:
        raise ValueError(f"Failed to place order for {symbol}")

# Implement other order functions similarly with appropriate error handling, memory efficiency, and performance optimizations.

@login_required
def order_option_spread(direction: str, price: float, symbol: str, quantity: int, spread: Dict[str, Any], account_number: Optional[str] = None, timeInForce: str = 'gtc', jsonify: bool = True) -> Dict[str, Any]:
    """Submits a limit order for an option spread."""
    try:
        symbol = symbol.upper().strip()
    except AttributeError as message:
        raise ValueError(f"Invalid symbol: {symbol}") from message

    legs = []
    for each in spread:
        optionID = id_for_option(symbol, each['expirationDate'], each['strike'], each['optionType'])
        legs.append({
            'position_effect': each['effect'],
            'side': each['action'],
            'ratio_quantity': each['ratio_quantity'],
            'option': option_instruments_url(optionID)
        })

    payload = {
        'account': load_account_profile(account_number=account_number, info='url'),
        'direction': direction,
        'time_in_force': timeInForce,
        'legs': legs,
        'type': 'limit',
        'trigger': 'immediate',
        'price': price,
        'quantity': quantity,
        'ref_id': str(uuid4()),
    }

    url = option_orders_url()
    data = request_post(url, payload, json=True, jsonify_data=jsonify)

    if data:
        return data
    else:
        raise ValueError(f"Failed to place {direction} spread order for {symbol}")

# Implement additional order functions as necessary.

