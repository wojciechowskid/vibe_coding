import logging

import sentry_sdk
from sentry_sdk.integrations.dramatiq import DramatiqIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from config.logging.log_properties import log_properties_registry
from config.settings import Environment, settings


def _before_send(event, hint):  # noqa: ARG001
    log_properties = log_properties_registry.get()
    if log_properties:
        event.setdefault('tags', {}).update(log_properties.flat_dump())
    return event


def configure_sentry_handler():
    if settings.SENTRY_DSN and settings.ENVIRONMENT != Environment.LOCAL:
        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            enable_tracing=True,
            integrations=[DramatiqIntegration(), LoggingIntegration(level=logging.INFO, event_level=logging.WARNING)],
            environment=str(settings.ENVIRONMENT),
            before_send=_before_send,
        )
