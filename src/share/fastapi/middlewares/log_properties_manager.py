from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from ddutils.scoped_registry import ScopedRegistry


class LogPropertiesManagerMiddleware:
    """
    Pure ASGI middleware that initializes LogProperties at the start of each HTTP request
    and clears them after the request is complete.

    LogProperties (request_id, headers, duration) become available
    to all loggers during the request via log_properties_registry.

    Important: Implemented as pure ASGI middleware (not BaseHTTPMiddleware)
    to avoid breaking context-dependent connection scoping.
    """

    def __init__(self, app: ASGIApp, log_properties_registry: ScopedRegistry):
        self.app = app
        self.log_properties_registry = log_properties_registry

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        try:
            headers = dict(Headers(scope=scope).items())
            await self.log_properties_registry(headers=headers)
            await self.app(scope, receive, send)
        finally:
            await self.log_properties_registry.clear()
