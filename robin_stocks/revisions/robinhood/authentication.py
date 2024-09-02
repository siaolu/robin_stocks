"""Contains all functions for the purpose of logging in and out to Robinhood."""
import getpass
import os
import pickle
import random
from functools import wraps
from threading import Lock

from robin_stocks.robinhood.helper import request_get, request_post, update_session, set_login_state, get_output
from robin_stocks.robinhood.urls import login_url, challenge_url, positions_url

# Global variables
_LOGIN_LOCK = Lock()
_SESSION_DATA = {}

def generate_device_token():
    """Generate a token used when logging in."""
    rands = [random.randint(0, 255) for _ in range(16)]
    hexa = [f"{i:02x}" for i in range(256)]
    return '-'.join([''.join(hexa[r] for r in rands[i:i+4]) for i in range(0, 16, 4)])

def respond_to_challenge(challenge_id, sms_code):
    """Post to the challenge url."""
    url = challenge_url(challenge_id)
    payload = {'response': sms_code}
    return request_post(url, payload)

def _load_cached_session(pickle_path):
    """Load session data from a pickle file."""
    try:
        with open(pickle_path, 'rb') as f:
            return pickle.load(f)
    except (IOError, pickle.UnpicklingError):
        return None

def _save_session_to_cache(pickle_path, session_data):
    """Save session data to a pickle file."""
    with open(pickle_path, 'wb') as f:
        pickle.dump(session_data, f)

def login(username=None, password=None, expiresIn=86400, scope='internal', by_sms=True, store_session=True, mfa_code=None, pickle_name=""):
    """Log the user into robinhood by getting an authentication token."""
    global _SESSION_DATA

    with _LOGIN_LOCK:
        device_token = generate_device_token()
        home_dir = os.path.expanduser("~")
        data_dir = os.path.join(home_dir, ".tokens")
        os.makedirs(data_dir, exist_ok=True)
        creds_file = f"robinhood{pickle_name}.pickle"
        pickle_path = os.path.join(data_dir, creds_file)

        # Try to load cached session
        if store_session and os.path.isfile(pickle_path):
            cached_session = _load_cached_session(pickle_path)
            if cached_session:
                _SESSION_DATA = cached_session
                set_login_state(True)
                update_session('Authorization', f"{_SESSION_DATA['token_type']} {_SESSION_DATA['access_token']}")
                
                # Verify the token is still valid
                try:
                    res = request_get(positions_url(), 'pagination', {'nonzero': 'true'}, jsonify_data=False)
                    res.raise_for_status()
                    return {**_SESSION_DATA, 'detail': f'Logged in using cached authentication in {creds_file}'}
                except Exception:
                    print("Cached session expired. Logging in again.", file=get_output())
                    set_login_state(False)
                    update_session('Authorization', None)

        # Prepare payload for login
        challenge_type = "sms" if by_sms else "email"
        payload = {
            'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
            'expires_in': expiresIn,
            'grant_type': 'password',
            'scope': scope,
            'challenge_type': challenge_type,
            'device_token': device_token
        }

        if mfa_code:
            payload['mfa_code'] = mfa_code

        # Get username and password if not provided
        if not username:
            username = input("Robinhood username: ")
        if not password:
            password = getpass.getpass("Robinhood password: ")

        payload['username'] = username
        payload['password'] = password

        # Attempt login
        url = login_url()
        data = request_post(url, payload)

        if not data:
            raise Exception('Error: Trouble connecting to Robinhood API. Check internet connection.')

        # Handle MFA and challenge cases
        if 'mfa_required' in data:
            data = _handle_mfa(url, payload)
        elif 'challenge' in data:
            data = _handle_challenge(url, payload, data['challenge']['id'])

        # Update session data
        if 'access_token' in data:
            _SESSION_DATA = {
                'token_type': data['token_type'],
                'access_token': data['access_token'],
                'refresh_token': data['refresh_token'],
                'device_token': device_token,
                'detail': "Logged in with new authentication code."
            }
            update_session('Authorization', f"{data['token_type']} {data['access_token']}")
            set_login_state(True)

            if store_session:
                _save_session_to_cache(pickle_path, _SESSION_DATA)
        else:
            raise Exception(data.get('detail', 'Unknown login error'))

        return _SESSION_DATA

def _handle_mfa(url, payload):
    """Handle Multi-Factor Authentication."""
    while True:
        mfa_token = input("Please enter the MFA code: ")
        payload['mfa_code'] = mfa_token
        res = request_post(url, payload, jsonify_data=False)
        if res.status_code == 200:
            return res.json()
        print("Incorrect MFA code. Please try again.", file=get_output())

def _handle_challenge(url, payload, challenge_id):
    """Handle login challenge."""
    while True:
        sms_code = input('Enter Robinhood code for validation: ')
        res = respond_to_challenge(challenge_id, sms_code)
        if 'challenge' not in res:
            update_session('X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
            return request_post(url, payload)
        if res['challenge']['remaining_attempts'] <= 0:
            raise Exception("Too many failed challenge attempts")
        print(f"Incorrect code. {res['challenge']['remaining_attempts']} attempts remaining.", file=get_output())

def login_required(func):
    """Decorator to ensure a function is only called when logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _SESSION_DATA:
            raise Exception("You must be logged in to use this function")
        return func(*args, **kwargs)
    return wrapper

@login_required
def logout():
    """Remove authorization from the session."""
    global _SESSION_DATA
    _SESSION_DATA = {}
    set_login_state(False)
    update_session('Authorization', None)

def get_session_data():
    """Retrieve current session data."""
    return _SESSION_DATA