"""API port interface for Users operations."""

from abc import ABC


class UsersAPIPort(ABC):
    """Port interface for Users API operations."""

    # This is a marker interface
    # The actual implementation is in the adapter using FastAPI routers
    pass
