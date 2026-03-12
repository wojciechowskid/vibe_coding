from collections.abc import Awaitable, Callable
from typing import Any

from share.dramatiq.actor_middlewares.base import BaseActorMiddleware


class CloseDBConnectionsMiddleware(BaseActorMiddleware):
    def __init__(self, close_db_connections: Callable[[], Awaitable[None]]):
        self.close_db_connections = close_db_connections

    async def __call__(self, call_next: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        try:
            return await call_next(*args, **kwargs)
        finally:
            await self.close_db_connections()
