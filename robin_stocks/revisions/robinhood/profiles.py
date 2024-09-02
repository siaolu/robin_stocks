"""Contains functions for getting all the information tied to a user account."""
from typing import Optional, Union, Dict, Any
from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.urls import *

@login_required
def load_account_profile(account_number: Optional[str] = None, info: Optional[str] = None, dataType: str = "indexzero") -> Union[Dict[str, Any], str]:
    """Gets the information associated with the account's profile, including day trading information and cash being held by Robinhood.
    
    :param account_number: The Robinhood account number.
    :param info: The name of the key whose value is to be returned from the function.
    :param dataType: Determines how to filter the data. 'indexzero' will return data['results'][0], 'regular' returns the unfiltered data, 'results' returns data['results'], 'pagination' returns data['results'] and appends it with any data in data['next'].
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = account_profile_url(account_number)
    data = request_get(url) if account_number else request_get(url, dataType)
    
    if not data:
        raise ValueError(f"Failed to load account profile for account number: {account_number}")
    
    return filter_data(data, info)

@login_required
def load_basic_profile(info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Gets the information associated with the personal profile, such as phone number, city, marital status, and date of birth.

    :param info: The name of the key whose value is to be returned from the function.
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = basic_profile_url()
    data = request_get(url)
    
    if not data:
        raise ValueError("Failed to load basic profile.")
    
    return filter_data(data, info)

@login_required
def load_investment_profile(info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Gets the information associated with the investment profile, including total net worth and risk tolerance.

    :param info: The name of the key whose value is to be returned from the function.
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = investment_profile_url()
    data = request_get(url)
    
    if not data:
        raise ValueError("Failed to load investment profile.")
    
    return filter_data(data, info)

@login_required
def load_portfolio_profile(account_number: Optional[str] = None, info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Gets the information associated with the portfolio's profile, such as withdrawable amount, market value of account, and excess margin.

    :param account_number: The Robinhood account number.
    :param info: The name of the key whose value is to be returned from the function.
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = portfolio_profile_url(account_number)
    data = request_get(url) if account_number else request_get(url, 'indexzero')
    
    if not data:
        raise ValueError(f"Failed to load portfolio profile for account number: {account_number}")
    
    return filter_data(data, info)

@login_required
def load_security_profile(info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Gets the information associated with the security profile, including security affiliation and stock loan consent status.

    :param info: The name of the key whose value is to be returned from the function.
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = security_profile_url()
    data = request_get(url)
    
    if not data:
        raise ValueError("Failed to load security profile.")
    
    return filter_data(data, info)

@login_required
def load_user_profile(info: Optional[str] = None) -> Union[Dict[str, Any], str]:
    """Gets the information associated with the user profile, such as username, email, and links to other profiles.

    :param info: The name of the key whose value is to be returned from the function.
    :returns: A dictionary of key/value pairs, or a string if `info` is provided.
    """
    url = user_profile_url()
    data = request_get(url)
    
    if not data:
        raise ValueError("Failed to load user profile.")
    
    return filter_data(data, info)

