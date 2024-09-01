# urls.py revision
# Rev 1.3 (experimental)
# Date: 2024-09-01
# Revised by: dasConnOps

from enum import Enum
from functools import lru_cache
import re

class Version(Enum):
    """Enum for different version types"""
    v1 = "v1"
    v2 = "v2"

class URLS:
    """Static class for holding all urls."""
    BASE_URL = "https://api.tdameritrade.com"
    
    def __init__(self):
        raise NotImplementedError(f"Cannot create instance of {self.__class__.__name__}")

    @classmethod
    @lru_cache(maxsize=None)
    def get_base_url(cls, version: Version) -> str:
        return f"{cls.BASE_URL}/{version.value}/"

    @staticmethod
    @lru_cache(maxsize=128)
    def get_endpoint(url: str) -> str:
        if not url.startswith(URLS.BASE_URL):
            raise ValueError("The URL has the wrong base.")
        return url[len(URLS.BASE_URL):]

    # accounts.py
    @classmethod
    def account(cls, id: str) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts/{id}"

    @classmethod
    def accounts(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts"

    @classmethod
    def transaction(cls, id: str, transaction: str) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts/{id}/transactions/{transaction}"

    @classmethod
    def transactions(cls, id: str) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts/{id}/transactions"

    # authentication.py
    @classmethod
    def oauth(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}oauth2/token"

    # markets.py
    @classmethod
    def markets(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/hours"

    @classmethod
    def market(cls, market: str) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/{market}/hours"

    @classmethod
    def movers(cls, index: str) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/{index}/movers"

    # orders.py
    @classmethod
    def orders(cls, account_id: str) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts/{account_id}/orders"

    @classmethod
    def order(cls, account_id: str, order_id: str) -> str:
        return f"{cls.get_base_url(Version.v1)}accounts/{account_id}/orders/{order_id}"

    # stocks.py
    @classmethod
    def instruments(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}instruments"

    @classmethod
    def instrument(cls, cusip: str) -> str:
        return f"{cls.get_base_url(Version.v1)}instruments/{cusip}"

    @classmethod
    def quote(cls, ticker: str) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/{ticker}/quotes"

    @classmethod
    def quotes(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/quotes"

    @classmethod
    def price_history(cls, ticker: str) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/{ticker}/pricehistory"

    @classmethod
    def option_chains(cls) -> str:
        return f"{cls.get_base_url(Version.v1)}marketdata/chains"