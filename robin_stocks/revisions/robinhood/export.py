"""Module for exporting Robinhood trade data to CSV files."""
from csv import DictWriter
from datetime import date
from pathlib import Path
from typing import Optional
from functools import wraps

from robin_stocks.robinhood.helper import login_required
from robin_stocks.robinhood.orders import get_all_stock_orders, get_all_crypto_orders, get_all_option_orders
from robin_stocks.robinhood.stocks import get_symbol_by_url
from robin_stocks.robinhood.crypto import get_crypto_quote_from_id

def ensure_csv_extension(file_name: str) -> Path:
    """Ensures the file name ends with .csv"""
    return Path(file_name).with_suffix('.csv').resolve()

def create_csv_path(dir_path: str, file_name: Optional[str], order_type: str) -> Path:
    """Creates a filepath for the CSV file."""
    directory = Path(dir_path).resolve()
    if not file_name:
        file_name = f"{order_type}_orders_{date.today().strftime('%Y-%m-%d')}.csv"
    return directory / ensure_csv_extension(file_name)

def safe_csv_write(func):
    """Decorator to handle file operations safely."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IOError as e:
            print(f"Error writing to CSV: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return wrapper

@login_required
@safe_csv_write
def export_completed_stock_orders(dir_path: str, file_name: Optional[str] = None):
    """Write all completed stock orders to a CSV file."""
    file_path = create_csv_path(dir_path, file_name, 'stock')
    all_orders = get_all_stock_orders()
    
    fieldnames = ['symbol', 'date', 'order_type', 'side', 'fees', 'quantity', 'average_price']
    
    with open(file_path, 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for order in all_orders:
            if order['state'] == 'cancelled' and order['executions']:
                for partial in order['executions']:
                    writer.writerow({
                        'symbol': get_symbol_by_url(order['instrument']),
                        'date': partial['timestamp'],
                        'order_type': order['type'],
                        'side': order['side'],
                        'fees': order['fees'],
                        'quantity': partial['quantity'],
                        'average_price': partial['price']
                    })
            elif order['state'] == 'filled' and order['cancel'] is None:
                writer.writerow({
                    'symbol': get_symbol_by_url(order['instrument']),
                    'date': order['last_transaction_at'],
                    'order_type': order['type'],
                    'side': order['side'],
                    'fees': order['fees'],
                    'quantity': order['quantity'],
                    'average_price': order['average_price']
                })

@login_required
@safe_csv_write
def export_completed_crypto_orders(dir_path: str, file_name: Optional[str] = None):
    """Write all completed crypto orders to a CSV file."""
    file_path = create_csv_path(dir_path, file_name, 'crypto')
    all_orders = get_all_crypto_orders()
    
    fieldnames = ['symbol', 'date', 'order_type', 'side', 'fees', 'quantity', 'average_price']
    
    with open(file_path, 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for order in all_orders:
            if order['state'] == 'filled' and order['cancel_url'] is None:
                writer.writerow({
                    'symbol': get_crypto_quote_from_id(order['currency_pair_id'], 'symbol'),
                    'date': order['last_transaction_at'],
                    'order_type': order['type'],
                    'side': order['side'],
                    'fees': order.get('fees', 0.0),
                    'quantity': order['quantity'],
                    'average_price': order['average_price']
                })

@login_required
@safe_csv_write
def export_completed_option_orders(dir_path: str, file_name: Optional[str] = None):
    """Write all completed option orders to a CSV file."""
    file_path = create_csv_path(dir_path, file_name, 'option')
    all_orders = get_all_option_orders()
    
    fieldnames = ['chain_symbol', 'expiration_date', 'strike_price', 'option_type', 'side',
                  'order_created_at', 'direction', 'order_quantity', 'order_type',
                  'opening_strategy', 'closing_strategy', 'price', 'processed_quantity']
    
    with open(file_path, 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for order in all_orders:
            if order['state'] == 'filled':
                for leg in order['legs']:
                    instrument_data = request_get(leg['option'])
                    writer.writerow({
                        'chain_symbol': order['chain_symbol'],
                        'expiration_date': instrument_data['expiration_date'],
                        'strike_price': instrument_data['strike_price'],
                        'option_type': instrument_data['type'],
                        'side': leg['side'],
                        'order_created_at': order['created_at'],
                        'direction': order['direction'],
                        'order_quantity': order['quantity'],
                        'order_type': order['type'],
                        'opening_strategy': order['opening_strategy'],
                        'closing_strategy': order['closing_strategy'],
                        'price': order['price'],
                        'processed_quantity': order['processed_quantity']
                    })