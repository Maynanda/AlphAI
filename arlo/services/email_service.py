"""
Email service wrapper using Python's built-in smtplib.
Sends weekly reports to managers or stakeholders.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, sender_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email

    def send_email(self, to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """
        Sends an email via SMTP.
        Returns True if successful, False otherwise.
        """
        if not self.smtp_server or not self.sender_email:
            logger.error("SMTP Configuration is incomplete. Check settings.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = to_email

        # Attach text body
        msg.attach(MIMEText(body_text, "plain"))

        # Attach html body if present
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        try:
            # Connect to SMTP Server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            
            # Start TLS if port is standard TLS/submission port (587)
            if self.smtp_port == 587:
                server.starttls()
                server.ehlo()

            # Login if username is provided
            if self.username:
                server.login(self.username, self.password)

            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()
            logger.info(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
