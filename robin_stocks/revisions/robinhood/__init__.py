# __init__.py revision
# Rev 1.3 (experimental)
# Date: 2024-09-01
# Revised by: dasConnOps

from .authentication import login, logout
from .helper import set_output, get_output, request_get, request_post, request_delete, request_document, update_session, filter_data

# Lazy imports
from importlib import import_module

def __getattr__(name):
    if name in ['build_holdings', 'build_user_profile', 'get_all_positions', 'get_open_stock_positions', 'get_watchlist_by_name']:
        return getattr(import_module('.account', __name__), name)
    elif name in ['get_crypto_currency_pairs', 'get_crypto_positions', 'get_crypto_quote']:
        return getattr(import_module('.crypto', __name__), name)
    elif name in ['export_completed_stock_orders', 'export_completed_option_orders', 'export_completed_crypto_orders']:
        return getattr(import_module('.export', __name__), name)
    elif name in ['get_market_today_hours', 'get_top_movers']:
        return getattr(import_module('.markets', __name__), name)
    elif name in ['find_options_by_expiration', 'get_option_market_data', 'get_all_option_positions']:
        return getattr(import_module('.options', __name__), name)
    elif name in ['order_buy_market', 'order_sell_market', 'order_buy_limit', 'order_sell_limit', 'get_all_open_stock_orders']:
        return getattr(import_module('.orders', __name__), name)
    elif name in ['load_account_profile', 'load_basic_profile', 'load_investment_profile']:
        return getattr(import_module('.profiles', __name__), name)
    elif name in ['get_quotes', 'get_fundamentals', 'get_instruments_by_symbols', 'get_latest_price']:
        return getattr(import_module('.stocks', __name__), name)
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    'login', 'logout', 'set_output', 'get_output', 'request_get', 'request_post', 
    'request_delete', 'request_document', 'update_session', 'filter_data'
]