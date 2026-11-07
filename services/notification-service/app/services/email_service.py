import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """The email could not be handed to the mail server. The event is retried, then dead-lettered."""


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> None:
        """Send one email. Raises EmailDeliveryError on failure so the caller never believes a lost email was sent."""
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', 'no-reply@staymatch.com')

        if not smtp_host or not smtp_user:
            # Development mode: nothing is sent. Set SMTP_HOST and SMTP_USER to deliver real emails.
            logger.info("[EMAIL NOT SENT - SMTP not configured] To: %s | Subject: %s", to_email, subject)
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
        except Exception as exc:
            raise EmailDeliveryError(f"Could not send email to {to_email}: {exc}") from exc
        logger.info("Email sent to %s", to_email)
