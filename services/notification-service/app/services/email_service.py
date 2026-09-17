import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', 'no-reply@staymatch.com')

        if not smtp_host or not smtp_user:
            logger.info(f"[DEV EMAIL LOG] To: {to_email} | Subject: {subject} | Body: {body[:100]}...")
            print(f"[EMAIL DISPATCH DISABLED] Set SMTP_HOST to send real emails. To: {to_email} | Subject: {subject}")
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email

            part = MIMEText(body, 'html' if is_html else 'plain')
            msg.attach(part)

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch email to {to_email}: {e}")
            return False

