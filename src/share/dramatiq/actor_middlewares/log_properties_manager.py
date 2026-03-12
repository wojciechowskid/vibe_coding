from functools import wraps

from ddutils.scoped_registry import ScopedRegistry


def log_properties_manager_decorator(log_properties_registry: ScopedRegistry):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await log_properties_registry()
            try:
                return await func(*args, **kwargs)
            finally:
                await log_properties_registry.clear()

        return wrapper

    return decorator
