from logging.config import dictConfig

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'config.logging.handlers.stdout.formatter.CustomJsonFormatter',
            'format': '%(levelname)s %(message)s %(name)s',
        }
    },
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'json'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        # handled errors
        'uvicorn.error': {'level': 'ERROR', 'propagate': False, 'handlers': ['console']},
        'uvicorn.access': {'level': 'INFO', 'propagate': False, 'handlers': []},
        'dramatiq': {'level': 'ERROR', 'propagate': False, 'handlers': ['console']},
        # skipped errors
        'httpx': {'level': 'INFO', 'propagate': False, 'handlers': []},
        'uvicorn': {'level': 'INFO', 'propagate': False, 'handlers': []},
        'watchfiles.main': {'level': 'INFO', 'propagate': False, 'handlers': []},
        'sqlalchemy.engine': {'level': 'INFO', 'propagate': False, 'handlers': []},
        'apscheduler.scheduler': {'level': 'INFO', 'propagate': False, 'handlers': []},
    },
}


def configure_stdout_handler():
    dictConfig(LOG_CONFIG)
