"""Perform dependenciese injection of Gmail Client API."""

import inbox_api

from ._impl import GmailClientImpl

__all__: list[str] = ["GmailClientImpl", "_impl"]

# Dependency Injection of this implementation into the API
#
def _new_client() -> inbox_api.GmailClientInterface:
    """Get a factory that returns a *fresh instance* each call."""
    return GmailClientImpl()

inbox_api.get_client = _new_client
