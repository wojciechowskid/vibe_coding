import logging
import os
from typing import Any, Protocol

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from ddutils.object_getter import get_object_by_path

logger = logging.getLogger(__name__)


class LogPropertiesRegistry(Protocol):
    """Async-callable scoped storage bound to the current coroutine/task.

    Initializes per-request properties (request_id, headers, duration, etc.)
    and makes them available to loggers throughout the request lifecycle.
    """

    async def __call__(self, **kwargs: Any) -> Any:
        ...

    async def clear(self) -> None:
        ...


log_properties_registry: LogPropertiesRegistry | None = get_object_by_path(os.getenv('LOG_PROPERTIES_REGISTRY_PATH'))


class LogPropertiesManagerMiddleware:
    """
    Pure ASGI middleware that initializes LogProperties at the start of each HTTP request
    and clears them after the request is complete.

    LogProperties (request_id, headers, duration) become available
    to all loggers during the request via log_properties_registry.

    Important: Implemented as pure ASGI middleware (not BaseHTTPMiddleware)
    to avoid breaking context-dependent connection scoping.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] != 'http' or not log_properties_registry:
            await self.app(scope, receive, send)
            if not log_properties_registry:
                logger.error(
                    {
                        'message': (
                            'Log properties registry is not defined. '
                            'Make sure the `LOG_PROPERTIES_REGISTRY_PATH` environment variable is set correctly.'
                        )
                    }
                )
            return

        try:
            headers = dict(Headers(scope=scope).items())
            await log_properties_registry(headers=headers)
            await self.app(scope, receive, send)
        finally:
            await log_properties_registry.clear()
