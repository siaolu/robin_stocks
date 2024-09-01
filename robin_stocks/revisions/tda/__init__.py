"""
Robin Stocks: A Python library for interacting with TD Ameritrade API.

This module provides a comprehensive interface for trading stocks, options,
and managing accounts through the TD Ameritrade platform.
"""

from typing import List
import importlib

__version__ = "1.0.0"  # Update this with your actual version number

__all__: List[str] = []

def __getattr__(name: str):
    """Lazy load modules and functions to improve import time."""
    if name in __all__:
        module_name, attr = _get_module_and_attr(name)
        module = importlib.import_module(f".{module_name}", __name__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def _get_module_and_attr(name: str):
    """Helper function to determine which module an attribute belongs to."""
    module_map = {
        'accounts': ['get_account', 'get_accounts', 'get_transaction', 'get_transactions'],
        'authentication': ['generate_encryption_passcode', 'login', 'login_first_time'],
        'helper': ['get_login_state', 'get_order_number', 'request_data', 'request_delete', 'request_get', 'request_headers', 'request_post'],
        'markets': ['get_hours_for_market', 'get_hours_for_markets', 'get_movers'],
        'orders': ['cancel_order', 'get_order', 'get_orders_for_account', 'place_order'],
        'stocks': ['get_instrument', 'get_option_chains', 'get_price_history', 'get_quote', 'get_quotes', 'search_instruments'],
    }
    for module, attrs in module_map.items():
        if name in attrs:
            return module, name
    raise ValueError(f"Unknown attribute: {name}")

# Populate __all__ with all available functions
for module_attrs in _get_module_and_attr.__closure__[0].cell_contents.values():
    __all__.extend(module_attrs)

# You can add any commonly used or important functions here for direct import
from .authentication import login, login_first_time

# Add version to __all__
__all__.append("__version__")