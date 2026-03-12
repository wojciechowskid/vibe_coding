import asyncio
import time
import uuid
from typing import Any

from pydantic import Field, computed_field

from dddesign.structure.domains.value_objects import ValueObject
from ddutils.scoped_registry import ScopedRegistry


class Headers(ValueObject):
    ip_address: str | None = Field(None, alias='x-forwarded-for')
    domain: str | None = Field(None, alias='host')


class LogProperties(ValueObject):
    request_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    start_time: float = Field(default_factory=time.time, exclude=True)
    headers: Headers | None = None

    @computed_field(return_type=float)
    def duration(self) -> float:
        return round(time.time() - self.start_time, 3)

    def flat_dump(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in self.model_dump(mode='json', exclude_none=True).items():
            if isinstance(value, dict):
                result.update({f'{key}.{nested_key}': nested_value for nested_key, nested_value in value.items()})
            else:
                result[key] = value
        return result


async def _create_log_properties(**kwargs: Any) -> LogProperties:
    return LogProperties.model_validate(kwargs)


log_properties_registry: ScopedRegistry[LogProperties] = ScopedRegistry[LogProperties](
    create_func=_create_log_properties, scope_func=asyncio.current_task
)
