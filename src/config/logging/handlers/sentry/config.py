import logging

import sentry_sdk
from sentry_sdk.integrations.dramatiq import DramatiqIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from config.settings import Environment, settings


def configure_sentry_handler():
    if settings.SENTRY_DSN and settings.ENVIRONMENT != Environment.LOCAL:
        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            enable_tracing=True,
            integrations=[DramatiqIntegration(), LoggingIntegration(level=logging.INFO, event_level=logging.WARNING)],
            environment=str(settings.ENVIRONMENT),
        )
