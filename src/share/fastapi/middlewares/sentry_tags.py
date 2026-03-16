import sentry_sdk
from pydantic import BaseModel
from starlette.types import ASGIApp, Receive, Scope, Send

from dddesign.utils.base_model import flatten_model_dump
from ddutils.annotation_helpers import is_subclass
from ddutils.scoped_registry import ScopedRegistry


class SentryTagsMiddleware:
    def __init__(self, app: ASGIApp, log_properties_registry: ScopedRegistry):
        if not is_subclass(log_properties_registry.generic_type, BaseModel):
            raise TypeError(f'Expected ScopedRegistry[BaseModel], got ScopedRegistry[{log_properties_registry.generic_type}]')
        self.app = app
        self.log_properties_registry = log_properties_registry

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] == 'http':
            log_properties = self.log_properties_registry.get()
            if log_properties:
                sentry_scope = sentry_sdk.get_current_scope()
                for key, value in flatten_model_dump(log_properties, mode='json', exclude_none=True).items():
                    sentry_scope.set_tag(key, value)

        await self.app(scope, receive, send)
