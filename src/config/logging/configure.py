from config.logging.handlers.sentry.config import configure_sentry_handler
from config.logging.handlers.stdout.config import configure_stdout_handler
from config.settings import settings


def configure_logging_handlers():
    if not settings.DEBUG:
        configure_stdout_handler()
        configure_sentry_handler()
