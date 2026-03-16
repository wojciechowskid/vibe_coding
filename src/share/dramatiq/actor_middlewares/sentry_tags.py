from collections.abc import Awaitable, Callable
from typing import Any

import sentry_sdk
from pydantic import BaseModel

from dddesign.utils.base_model import flatten_model_dump
from ddutils.annotation_helpers import is_subclass
from ddutils.scoped_registry import ScopedRegistry

from share.dramatiq.actor_middlewares.base import BaseActorMiddleware


class SentryTagsMiddleware(BaseActorMiddleware):
    def __init__(self, log_properties_registry: ScopedRegistry):
        if not is_subclass(log_properties_registry.generic_type, BaseModel):
            raise TypeError(f'Expected ScopedRegistry[BaseModel], got ScopedRegistry[{log_properties_registry.generic_type}]')
        self.log_properties_registry = log_properties_registry

    async def __call__(self, call_next: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        log_properties = self.log_properties_registry.get()
        if log_properties:
            sentry_scope = sentry_sdk.get_current_scope()
            for key, value in flatten_model_dump(log_properties, mode='json', exclude_none=True).items():
                sentry_scope.set_tag(key, value)
        return await call_next(*args, **kwargs)
