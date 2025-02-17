"""
This module contains a class that can be used to redirect the output of the
sys.stderr to the standard ``logging``. This is required because by default the
sys.stderr = None. With the configuration of ``hydro_mt``, where ``faulthandler``
is enabled, the sys.stderr is required. Without the redirection of the sys.stderr
to the FaultHandlerToLogging, the ``hydro_mt`` will crash on import.
"""

import sys
import logging


class FaultHandlerToLogging:
    """Class to redirect the output of the sys.stderr to the standard Python 
    ``logging`` module."""

    def __init__(self, level):
        self.level = level

    def write(self, message: str):
        """Writes a message to logger. The message is split on newlines.

        Args:
            message (str): The message to write to the logger.
        """
        if message != '\n':
            self.level(message)

    def flush(self):
        """Required to mimick a filehandler """
        return None

    def fileno(self):
        """Required to mimick a filehandler """
        return 2


def stderr_to_logging():
    """Redirects the sys.stderr to the standard Python ``logging`` module."""
    sys.stderr = FaultHandlerToLogging(logging.error)
