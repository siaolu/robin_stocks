"""Manages global variables and session information for the Robinhood API client."""

import sys
from typing import TextIO, Optional
from requests import Session
from threading import Lock

class RobinhoodGlobals:
    """Encapsulates global variables and session information."""

    def __init__(self):
        self._logged_in: bool = False
        self._login_lock: Lock = Lock()
        self._session: Session = self._create_session()
        self._output: TextIO = sys.stdout

    @property
    def logged_in(self) -> bool:
        """Indicates whether the user is logged in."""
        return self._logged_in

    @logged_in.setter
    def logged_in(self, value: bool):
        with self._login_lock:
            self._logged_in = value

    @property
    def session(self) -> Session:
        """Returns the current session object."""
        return self._session

    @property
    def output(self) -> TextIO:
        """Returns the current output stream."""
        return self._output

    @output.setter
    def output(self, stream: TextIO):
        """Sets the output stream for print statements."""
        if not hasattr(stream, 'write'):
            raise ValueError("Output stream must have a 'write' method.")
        self._output = stream

    def _create_session(self) -> Session:
        """Creates and configures a new session object."""
        session = Session()
        session.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Accept-Language": "en-US,en;q=1",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.431.4",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        })
        return session

    def reset_session(self):
        """Resets the session object."""
        self._session = self._create_session()

# Global instance of RobinhoodGlobals
robinhood_globals = RobinhoodGlobals()

# Convenience functions for accessing global properties
def is_logged_in() -> bool:
    """Returns whether the user is logged in."""
    return robinhood_globals.logged_in

def set_logged_in(value: bool):
    """Sets the logged-in state."""
    robinhood_globals.logged_in = value

def get_session() -> Session:
    """Returns the current session object."""
    return robinhood_globals.session

def get_output() -> TextIO:
    """Returns the current output stream."""
    return robinhood_globals.output

def set_output(stream: TextIO):
    """Sets the output stream for print statements."""
    robinhood_globals.output = stream

def reset_session():
    """Resets the session object."""
    robinhood_globals.reset_session()