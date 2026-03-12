from collections.abc import Awaitable, Callable
from functools import wraps


def close_db_connections_decorator(close_db_connections: Callable[[], Awaitable[None]]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            finally:
                await close_db_connections()

        return wrapper

    return decorator
