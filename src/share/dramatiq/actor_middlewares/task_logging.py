import logging
from functools import wraps

from dramatiq import Retry

logger = logging.getLogger(__name__)


def task_logging_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        task_name = func.__name__
        params = _get_filtered_params(func, args, kwargs)

        logger.info({'message': f'Started task {task_name}', **params})
        try:
            result = await func(*args, **kwargs)
        except Retry:
            raise
        except Exception:
            logger.info({'message': f'Failed task {task_name}', **params})
            raise

        logger.info({'message': f'Finished task {task_name}', **({'result': result} if result is not None else {}), **params})
        return result

    return wrapper


def _get_filtered_params(fn, args, kwargs):
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
