from collections.abc import Awaitable, Callable

from starlette.types import ASGIApp, Receive, Scope, Send


class DBConnectionsCloserMiddleware:
    """
    Middleware responsible for closing database connections after each HTTP request.

    Important: This middleware is implemented as a pure ASGI middleware rather than using
    `starlette.middleware.base.BaseHTTPMiddleware`, because BaseHTTPMiddleware wraps `call_next`
    in a new asyncio.Task, which breaks context-dependent connection scoping (e.g., when using
    asyncio.current_task() as a scope key for scoped registries).
    """

    def __init__(self, app: ASGIApp, close_db_connections: Callable[[], Awaitable[None]]):
        self.app = app
        self.close_db_connections = close_db_connections

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        try:
            await self.app(scope, receive, send)
        finally:
            await self.close_db_connections()
