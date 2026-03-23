from datetime import timedelta

import dramatiq

from ddutils.convertors import convert_timedelta_to_milliseconds

from app.auth_context.applications.email_notification import email_notification_app_impl


@dramatiq.actor(
    queue_name='auth_context',
    priority=0,
    max_retries=3,
    min_backoff=convert_timedelta_to_milliseconds(timedelta(seconds=30)),
    max_backoff=convert_timedelta_to_milliseconds(timedelta(minutes=1)),
    max_age=convert_timedelta_to_milliseconds(timedelta(minutes=5)),
    time_limit=convert_timedelta_to_milliseconds(timedelta(minutes=1)),
)
async def email_notification_send_registration_email_task(email: str):
    await email_notification_app_impl.send_registration_email(email=email)
