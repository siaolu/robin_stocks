"""Holds the session header and other global variables."""
import os
from typing import Dict, Any
from requests import Session

class Config:
    """Configuration class for global settings."""
    DATA_DIR_NAME: str = ".tokens"
    PICKLE_NAME: str = "tda.pickle"
    RETURN_PARSED_JSON_RESPONSE: bool = False
    LOGGED_IN: bool = False
    API_HOST: str = "api.tdameritrade.com"
    USER_AGENT: str = os.environ.get("TDA_USER_AGENT", "*")

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

def create_session() -> Session:
    """Create and return a new session with default headers."""
    session = Session()
    session.headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US",
        "Host": Config.API_HOST,
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": Config.USER_AGENT,
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    return session

# The session object for making get and post requests.
SESSION: Session = create_session()

def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    return Config.to_dict()

def update_config(**kwargs: Any) -> None:
    """Update the configuration with the provided key-value pairs."""
    for key, value in kwargs.items():
        if hasattr(Config, key):
            setattr(Config, key, value)
        else:
            raise AttributeError(f"Configuration has no attribute '{key}'")

def reset_session() -> None:
    """Reset the global session object."""
    global SESSION
    SESSION = create_session()