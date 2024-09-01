import aiohttp
import asyncio
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
import logging
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential

from robin_stocks.tda.helper import format_inputs, login_required, TDAAPIError
from robin_stocks.tda.urls import URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Market(Enum):
    EQUITY = "EQUITY"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    BOND = "BOND"
    FOREX = "FOREX"

class MarketIndex(Enum):
    DJI = "$DJI"
    COMPX = "$COMPX"
    SPX = "$SPX.X"

class Direction(Enum):
    UP = "up"
    DOWN = "down"

class ChangeType(Enum):
    PERCENT = "percent"
    VALUE = "value"

def validate_date(date: str) -> None:
    """Validate the date string format."""
    from datetime import datetime
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        try:
            datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD'T'HH:MM:SSZ")

class TDAClientSession:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with getattr(self.session, method)(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                raise TDAAPIError("Rate limit exceeded")
            elif e.status >= 500:
                raise TDAAPIError("Server error")
            else:
                raise TDAAPIError(f"API error: {e.status}")
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise TDAAPIError(f"API request failed: {e}")

@login_required
@format_inputs
async def get_hours_for_markets(markets: Union[List[Market], str], date: str) -> Dict:
    """Gets market hours for various markets."""
    validate_date(date)
    if isinstance(markets, list):
        markets = ",".join(market.value for market in markets)
    elif isinstance(markets, str):
        markets = ",".join(Market(m.strip().upper()).value for m in markets.split(","))
    else:
        raise ValueError("markets must be a list of Market enums or a comma-separated string")

    url = URLS.markets()
    params = {"markets": markets, "date": date}
    
    async with TDAClientSession() as client:
        return await client.request('get', url, params=params)

@login_required
@format_inputs
@lru_cache(maxsize=128)
async def get_hours_for_market(market: Union[Market, str], date: str) -> Dict:
    """Gets market hours for a specific market."""
    validate_date(date)
    if isinstance(market, str):
        market = Market(market.upper()).value
    elif isinstance(market, Market):
        market = market.value
    else:
        raise ValueError("market must be a Market enum or a string")

    url = URLS.market(market)
    params = {"date": date}
    
    async with TDAClientSession() as client:
        return await client.request('get', url, params=params)

@login_required
@format_inputs
async def get_movers(market: Union[MarketIndex, str], direction: Union[Direction, str], change: Union[ChangeType, str]) -> Dict:
    """Gets market movers for a specific market."""
    if isinstance(market, str):
        market = MarketIndex(market.upper()).value
    elif isinstance(market, MarketIndex):
        market = market.value
    else:
        raise ValueError("market must be a MarketIndex enum or a string")

    if isinstance(direction, str):
        direction = Direction(direction.lower()).value
    elif isinstance(direction, Direction):
        direction = direction.value
    else:
        raise ValueError("direction must be a Direction enum or a string")

    if isinstance(change, str):
        change = ChangeType(change.lower()).value
    elif isinstance(change, ChangeType):
        change = change.value
    else:
        raise ValueError("change must be a ChangeType enum or a string")

    url = URLS.movers(market)
    params = {"direction": direction, "change": change}
    
    async with TDAClientSession() as client:
        return await client.request('get', url, params=params)

# Unit tests

import unittest
from unittest.mock import patch, MagicMock

class TestMarkets(unittest.TestCase):

    @patch('aiohttp.ClientSession.get')
    async def test_get_hours_for_markets(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"EQUITY": {"EQ": "09:30:00 - 16:00:00"}}
        mock_get.return_value.__aenter__.return_value = mock_response

        async with TDAClientSession() as client:
            result = await get_hours_for_markets([Market.EQUITY], "2024-09-01")
        self.assertEqual(result, {"EQUITY": {"EQ": "09:30:00 - 16:00:00"}})

    @patch('aiohttp.ClientSession.get')
    async def test_get_hours_for_market(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"EQUITY": {"EQ": "09:30:00 - 16:00:00"}}
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await get_hours_for_market(Market.EQUITY, "2024-09-01")
        self.assertEqual(result, {"EQUITY": {"EQ": "09:30:00 - 16:00:00"}})

        # Test caching
        cached_result = await get_hours_for_market(Market.EQUITY, "2024-09-01")
        self.assertEqual(cached_result, result)
        mock_get.assert_called_once()  # Ensure the API was only called once

    @patch('aiohttp.ClientSession.get')
    async def test_get_movers(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = [{"symbol": "AAPL", "change": 1.5}]
        mock_get.return_value.__aenter__.return_value = mock_response

        async with TDAClientSession() as client:
            result = await get_movers(MarketIndex.DJI, Direction.UP, ChangeType.PERCENT)
        self.assertEqual(result, [{"symbol": "AAPL", "change": 1.5}])

    def test_validate_date(self):
        validate_date("2024-09-01")  # Should not raise an exception
        validate_date("2024-09-01T12:00:00Z")  # Should not raise an exception
        with self.assertRaises(ValueError):
            validate_date("2024/09/01")  # Invalid format

    @patch('aiohttp.ClientSession.get')
    async def test_error_handling(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=MagicMock(),
            status=429
        )
        mock_get.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(TDAAPIError) as context:
            async with TDAClientSession() as client:
                await get_hours_for_markets([Market.EQUITY], "2024-09-01")
        
        self.assertTrue("Rate limit exceeded" in str(context.exception))

if __name__ == '__main__':
    unittest.main()