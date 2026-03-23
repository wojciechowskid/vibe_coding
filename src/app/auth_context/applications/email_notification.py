from dddesign.structure.applications import Application


class EmailNotificationApp(Application):
    async def send_registration_email(self, email: str) -> None:
        print(f'Sending registration email to {email}')


email_notification_app_impl = EmailNotificationApp()
