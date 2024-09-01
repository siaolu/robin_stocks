import pickle
from datetime import datetime, timedelta
from pathlib import Path
import logging
import keyring

from cryptography.fernet import Fernet
from robin_stocks.tda.globals import DATA_DIR_NAME, PICKLE_NAME
from robin_stocks.tda.helper import request_data, set_login_state, update_session
from robin_stocks.tda.urls import URLS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

def encrypt_data(cipher_suite: Fernet, data: str) -> bytes:
    """Encrypt the given data using the provided cipher suite."""
    return cipher_suite.encrypt(data.encode())

def decrypt_data(cipher_suite: Fernet, data: bytes) -> str:
    """Decrypt the given data using the provided cipher suite."""
    return cipher_suite.decrypt(data).decode()

def get_cipher_suite(encryption_passcode: str) -> Fernet:
    """Create and return a Fernet cipher suite."""
    if isinstance(encryption_passcode, str):
        encryption_passcode = encryption_passcode.encode()
    return Fernet(encryption_passcode)

def get_pickle_path() -> Path:
    """Get the path to the pickle file, creating necessary directories if they don't exist."""
    data_dir = Path.home().joinpath(DATA_DIR_NAME)
    data_dir.mkdir(parents=True, exist_ok=True)
    pickle_path = data_dir.joinpath(PICKLE_NAME)
    pickle_path.touch(exist_ok=True)
    return pickle_path

def login_first_time(encryption_passcode: str, client_id: str, authorization_token: str, refresh_token: str) -> None:
    """Store login information securely."""
    cipher_suite = get_cipher_suite(encryption_passcode)
    pickle_path = get_pickle_path()

    encrypted_data = {
        'authorization_token': encrypt_data(cipher_suite, authorization_token),
        'refresh_token': encrypt_data(cipher_suite, refresh_token),
        'client_id': encrypt_data(cipher_suite, client_id),
        'authorization_timestamp': datetime.now(),
        'refresh_timestamp': datetime.now()
    }

    with pickle_path.open("wb") as pickle_file:
        pickle.dump(encrypted_data, pickle_file)

    # Store encryption passcode securely
    keyring.set_password("robin_stocks", "encryption_passcode", encryption_passcode)

    logger.info("Login information stored successfully.")

def login(encryption_passcode: str) -> str:
    """Set the authorization token for API use."""
    cipher_suite = get_cipher_suite(encryption_passcode)
    pickle_path = get_pickle_path()

    try:
        with pickle_path.open("rb") as pickle_file:
            pickle_data = pickle.load(pickle_file)
    except FileNotFoundError:
        raise AuthenticationError("Please call login_first_time() to create pickle file.")

    access_token = decrypt_data(cipher_suite, pickle_data['authorization_token'])
    refresh_token = decrypt_data(cipher_suite, pickle_data['refresh_token'])
    client_id = decrypt_data(cipher_suite, pickle_data['client_id'])
    authorization_timestamp = pickle_data['authorization_timestamp']
    refresh_timestamp = pickle_data['refresh_timestamp']

    authorization_delta = timedelta(minutes=30)
    refresh_delta = timedelta(days=60)
    url = URLS.oauth()

    if datetime.now() - refresh_timestamp > refresh_delta:
        logger.info("Refresh token expired. Obtaining new refresh and authorization tokens.")
        payload = {
            "grant_type": "refresh_token",
            "access_type": "offline",
            "refresh_token": refresh_token,
            "client_id": client_id
        }
        data, _ = request_data(url, payload, True)
        if "access_token" not in data or "refresh_token" not in data:
            raise AuthenticationError("Refresh token is no longer valid. Call login_first_time() to get a new refresh token.")
        access_token, refresh_token = data["access_token"], data["refresh_token"]
        update_pickle_file(pickle_path, cipher_suite, access_token, refresh_token, client_id)
    elif datetime.now() - authorization_timestamp > authorization_delta:
        logger.info("Authorization token expired. Obtaining new authorization token.")
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id
        }
        data, _ = request_data(url, payload, True)
        if "access_token" not in data:
            raise AuthenticationError("Refresh token is no longer valid. Call login_first_time() to get a new refresh token.")
        access_token = data["access_token"]
        update_pickle_file(pickle_path, cipher_suite, access_token, refresh_token, client_id, refresh_timestamp)

    auth_token = f"Bearer {access_token}"
    update_session("Authorization", auth_token)
    update_session("apikey", client_id)
    set_login_state(True)
    logger.info("Login successful.")
    return auth_token

def update_pickle_file(pickle_path: Path, cipher_suite: Fernet, access_token: str, refresh_token: str, client_id: str, refresh_timestamp: datetime = None) -> None:
    """Update the pickle file with new token information."""
    with pickle_path.open("wb") as pickle_file:
        pickle.dump({
            'authorization_token': encrypt_data(cipher_suite, access_token),
            'refresh_token': encrypt_data(cipher_suite, refresh_token),
            'client_id': encrypt_data(cipher_suite, client_id),
            'authorization_timestamp': datetime.now(),
            'refresh_timestamp': refresh_timestamp or datetime.now()
        }, pickle_file)

def generate_encryption_passcode() -> str:
    """Generate and return an encryption key."""
    return Fernet.generate_key().decode()