import logging
from collections.abc import Awaitable, Callable
from typing import Any

from dramatiq import Retry

from share.dramatiq.actor_middlewares.base import BaseActorMiddleware

logger = logging.getLogger(__name__)


def _get_filtered_params(fn: Callable, args: tuple, kwargs: dict) -> dict:
    try:
        params = {
            **{
                attribute_name: args[item]
                for item, attribute_name in enumerate(tuple(fn.__annotations__.keys())[: len(args)], start=0)
            },
            **kwargs,
        }
        for key in list(params.keys()):
            if isinstance(params.get(key), (list, tuple, set, dict)):
                params.pop(key)
        return params
    except Exception as e:  # noqa: BLE001
        logger.error({'message': 'Getting params in dramatiq task failed', 'error': str(e)})
        return {}


class TaskLoggingMiddleware(BaseActorMiddleware):
    async def __call__(self, call_next: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        task_name = call_next.__name__  # ty: ignore[unresolved-attribute]
        params = _get_filtered_params(call_next, args, kwargs)

        logger.info({'message': f'Started task {task_name}', **params})
        try:
            result = await call_next(*args, **kwargs)
        except Retry:
            raise
        except Exception:
            logger.info({'message': f'Failed task {task_name}', **params})
            raise

        logger.info({'message': f'Finished task {task_name}', **({'result': result} if result is not None else {}), **params})
        return result
