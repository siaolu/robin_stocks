import asyncio
import functools
import json
import logging
from typing import Any, Dict, Tuple, Optional
from functools import wraps
from inspect import signature
import re

import aiohttp
import requests
from robin_stocks.tda.globals import (LOGGED_IN, RETURN_PARSED_JSON_RESPONSE, SESSION)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TDAAPIError(Exception):
    """Custom exception for TDA API errors."""
    pass

@functools.lru_cache(maxsize=128)
def get_order_number(data: Any) -> str:
    """Get the order number from the response data."""
    try:
        if isinstance(data, requests.models.Response):
            parse_string = data.headers["Location"]
        elif isinstance(data, (dict, requests.structures.CaseInsensitiveDict)):
            parse_string = data["Location"]
        else:
            parse_string = data
        
        order_id = re.split("orders/", parse_string, flags=re.IGNORECASE)[-1]
        return order_id
    except Exception as e:
        raise ValueError(f"Failed to extract order number: {e}")

def format_inputs(func):
    """Decorator for formatting inputs."""
    @wraps(func)
    def format_wrapper(*args, **kwargs):
        bound_args = signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        target_args = dict(bound_args.arguments)
        if target_args['jsonify'] is None:
            kwargs["jsonify"] = get_default_json_flag()
        return func(*args, **kwargs)
    return format_wrapper

def set_default_json_flag(parse_json: bool) -> None:
    """Sets whether you want all functions to return the json parsed response or not."""
    global RETURN_PARSED_JSON_RESPONSE
    RETURN_PARSED_JSON_RESPONSE = parse_json

def get_default_json_flag() -> bool:
    """Gets the boolean flag on the default JSON setting."""
    return RETURN_PARSED_JSON_RESPONSE

def update_session(key: str, value: str) -> None:
    """Updates the session header used by the requests library."""
    SESSION.headers[key] = value

def set_login_state(logged_in: bool) -> None:
    """Sets the login state"""
    global LOGGED_IN
    LOGGED_IN = logged_in

def get_login_state() -> bool:
    """Gets the login state"""
    return LOGGED_IN

def login_required(func):
    """Decorator for indicating which methods require the user to be logged in."""
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        if not get_login_state():
            raise TDAAPIError(f'{func.__name__} can only be called when logged in')
        return func(*args, **kwargs)
    return login_wrapper

async def async_request(method: str, url: str, **kwargs) -> Tuple[Any, Optional[Exception]]:
    """Asynchronous request function."""
    async with aiohttp.ClientSession() as session:
        try:
            async with getattr(session, method)(url, **kwargs) as response:
                response.raise_for_status()
                if kwargs.get('parse_json', False):
                    return await response.json(), None
                else:
                    return response, None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None, e

def request(method: str, url: str, payload: Dict[str, Any] = None, parse_json: bool = False) -> Tuple[Any, Optional[Exception]]:
    """Generic function for sending requests."""
    try:
        response = getattr(SESSION, method)(url, params=payload if method == 'get' else None, data=json.dumps(payload) if method != 'get' else None)
        response.raise_for_status()
        if parse_json:
            return response.json(), None
        else:
            return response, None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None, e

request_get = functools.partial(request, 'get')
request_post = functools.partial(request, 'post')
request_delete = functools.partial(request, 'delete')

async def async_request_get(*args, **kwargs):
    return await async_request('get', *args, **kwargs)

async def async_request_post(*args, **kwargs):
    return await async_request('post', *args, **kwargs)

async def async_request_delete(*args, **kwargs):
    return await async_request('delete', *args, **kwargs)

def request_data(url: str, payload: Dict[str, Any], parse_json: bool) -> Tuple[Any, Optional[Exception]]:
    """Function for sending a post request without using Session information."""
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        if parse_json:
            return response.json(), None
        else:
            return response, None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None, e

def request_headers(url: str, payload: Dict[str, Any], parse_json: bool) -> Tuple[Any, Optional[Exception]]:
    """Function for sending a post request with payload in headers."""
    try:
        response = SESSION.post(url, data=json.dumps(payload))
        response.raise_for_status()
        if parse_json:
            return response.headers, None
        else:
            return response, None
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None, e