import asyncio
from typing import Dict, Any, Optional, Union, List
from enum import Enum
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
import unittest
from unittest.mock import patch, MagicMock

from robin_stocks.tda.helper import format_inputs, login_required, TDAAPIError
from robin_stocks.tda.urls import URLS

class OrderStatus(Enum):
    AWAITING_PARENT_ORDER = "AWAITING_PARENT_ORDER"
    AWAITING_CONDITION = "AWAITING_CONDITION"
    AWAITING_MANUAL_REVIEW = "AWAITING_MANUAL_REVIEW"
    ACCEPTED = "ACCEPTED"
    AWAITING_UR_OUT = "AWAITING_UR_OUT"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    QUEUED = "QUEUED"
    WORKING = "WORKING"
    REJECTED = "REJECTED"
    PENDING_CANCEL = "PENDING_CANCEL"
    CANCELED = "CANCELED"
    PENDING_REPLACE = "PENDING_REPLACE"
    REPLACED = "REPLACED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"

class TDAClientSession:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
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
            raise TDAAPIError(f"API request failed: {e}")

@login_required
@format_inputs
async def place_order(account_id: str, order_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Place an order for a given account.

    :param account_id: The account id.
    :param order_payload: A dictionary of key-value pairs for the order information.
    :return: A dictionary containing the response from the API.
    :raises TDAAPIError: If the API request fails.
    """
    url = URLS.orders(account_id)
    async with TDAClientSession() as client:
        return await client.request('post', url, json=order_payload)

@login_required
@format_inputs
async def cancel_order(account_id: str, order_id: str) -> Dict[str, Any]:
    """
    Cancel an order for a given account.

    :param account_id: The account id.
    :param order_id: The order id.
    :return: A dictionary containing the response from the API.
    :raises TDAAPIError: If the API request fails.
    """
    url = URLS.order(account_id, order_id)
    async with TDAClientSession() as client:
        return await client.request('delete', url)

@login_required
@format_inputs
@lru_cache(maxsize=128)
async def get_order(account_id: str, order_id: str) -> Dict[str, Any]:
    """
    Gets information for an order for a given account.

    :param account_id: The account id.
    :param order_id: The order id.
    :return: A dictionary containing the order information.
    :raises TDAAPIError: If the API request fails.
    """
    url = URLS.order(account_id, order_id)
    async with TDAClientSession() as client:
        return await client.request('get', url)

@login_required
@format_inputs
async def get_orders_for_account(
    account_id: str,
    max_results: Optional[int] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    status: Optional[Union[OrderStatus, str]] = None
) -> Dict[str, Any]:
    """
    Gets all the orders for a given account.

    :param account_id: The account id.
    :param max_results: The max number of orders to retrieve.
    :param from_time: Specifies that no orders entered before this time should be returned. Format: yyyy-MM-dd.
    :param to_time: Specifies that no orders entered after this time should be returned. Format: yyyy-MM-dd.
    :param status: Specifies that only orders of this status should be returned.
    :return: A dictionary containing the list of orders.
    :raises TDAAPIError: If the API request fails.
    :raises ValueError: If the input parameters are invalid.
    """
    url = URLS.orders(account_id)
    payload = {}
    if max_results:
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("max_results must be a positive integer")
        payload["maxResults"] = max_results
    if from_time:
        payload["fromEnteredTime"] = from_time
    if to_time:
        payload["toEnteredTime"] = to_time
    if status:
        if isinstance(status, OrderStatus):
            payload["status"] = status.value
        elif isinstance(status, str) and status in OrderStatus.__members__:
            payload["status"] = status
        else:
            raise ValueError("Invalid status value")

    async with TDAClientSession() as client:
        return await client.request('get', url, params=payload)

@login_required
@format_inputs
async def place_bulk_orders(account_id: str, order_payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Place multiple orders for a given account in a single API call.

    :param account_id: The account id.
    :param order_payloads: A list of dictionaries, each containing the order information for a single order.
    :return: A list of dictionaries, each containing the response from the API for a single order.
    :raises TDAAPIError: If the API request fails.
    """
    url = URLS.orders(account_id)
    async with TDAClientSession() as client:
        return await client.request('post', url, json=order_payloads)

# Synchronous versions of the functions for backwards compatibility

def sync_place_order(account_id: str, order_payload: Dict[str, Any]) -> Dict[str, Any]:
    return asyncio.run(place_order(account_id, order_payload))

def sync_cancel_order(account_id: str, order_id: str) -> Dict[str, Any]:
    return asyncio.run(cancel_order(account_id, order_id))

def sync_get_order(account_id: str, order_id: str) -> Dict[str, Any]:
    return asyncio.run(get_order(account_id, order_id))

def sync_get_orders_for_account(
    account_id: str,
    max_results: Optional[int] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
    status: Optional[Union[OrderStatus, str]] = None
) -> Dict[str, Any]:
    return asyncio.run(get_orders_for_account(account_id, max_results, from_time, to_time, status))

def sync_place_bulk_orders(account_id: str, order_payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return asyncio.run(place_bulk_orders(account_id, order_payloads))

# Unit tests

class TestOrders(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.mock_session = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.raise_for_status = MagicMock()
        self.mock_response.json.return_value = {"orderId": "123"}
        self.mock_session.post = MagicMock(return_value=self.mock_response)
        self.mock_session.get = MagicMock(return_value=self.mock_response)
        self.mock_session.delete = MagicMock(return_value=self.mock_response)

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_place_order(self, mock_session):
        mock_session.return_value.__aenter__.return_value = self.mock_session
        result = await place_order("account123", {"symbol": "AAPL", "quantity": 100})
        self.assertEqual(result, {"orderId": "123"})
        self.mock_session.post.assert_called_once()

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_cancel_order(self, mock_session):
        mock_session.return_value.__aenter__.return_value = self.mock_session
        result = await cancel_order("account123", "order123")
        self.assertEqual(result, {"orderId": "123"})
        self.mock_session.delete.assert_called_once()

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_get_order(self, mock_session):
        mock_session.return_value.__aenter__.return_value = self.mock_session
        result = await get_order("account123", "order123")
        self.assertEqual(result, {"orderId": "123"})
        self.mock_session.get.assert_called_once()

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_get_orders_for_account(self, mock_session):
        mock_session.return_value.__aenter__.return_value = self.mock_session
        result = await get_orders_for_account("account123", max_results=10, status=OrderStatus.FILLED)
        self.assertEqual(result, {"orderId": "123"})
        self.mock_session.get.assert_called_once()

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_place_bulk_orders(self, mock_session):
        mock_session.return_value.__aenter__.return_value = self.mock_session
        orders = [{"symbol": "AAPL", "quantity": 100}, {"symbol": "GOOGL", "quantity": 50}]
        result = await place_bulk_orders("account123", orders)
        self.assertEqual(result, {"orderId": "123"})
        self.mock_session.post.assert_called_once()

    async def test_invalid_status(self):
        with self.assertRaises(ValueError):
            await get_orders_for_account("account123", status="INVALID_STATUS")

    @patch('aiohttp.ClientSession', return_value=MagicMock())
    async def test_rate_limit_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=MagicMock(),
            status=429
        )
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        with self.assertRaises(TDAAPIError) as context:
            await place_order("account123", {"symbol": "AAPL", "quantity": 100})
        
        self.assertTrue("Rate limit exceeded" in str(context.exception))

if __name__ == '__main__':
    unittest.main()