"""
Email Confirmation Service for Site Visits
Sends branded, responsive HTML confirmation emails with meeting details,
calendar links, and sales consultant contact information.
"""

from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.config.settings import settings
from app.core.logging import logger


class EmailService:
    """Service for sending booking confirmation and real estate notification emails."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "visits@prestigerealty.com")

    def build_booking_email_html(
        self,
        customer_name: str,
        property_name: str,
        location: str,
        scheduled_date_str: str,
        scheduled_time_str: str,
        booking_ref: str,
        reschedule_url: Optional[str] = None,
    ) -> str:
        """Generates a responsive HTML email for site visit confirmation."""
        resched_link = reschedule_url or settings.CAL_COM_BOOKING_URL
        broker_name = settings.BROKER_NAME
        broker_phone = settings.BROKER_PHONE

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Prestige Realty Site Visit Confirmation</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7f9fa; margin: 0; padding: 24px; color: #1e293b; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
    .header {{ background: linear-gradient(135deg, #1e3a8a, #0f172a); color: #ffffff; padding: 32px 24px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
    .content {{ padding: 32px 24px; }}
    .greeting {{ font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #0f172a; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0; }}
    .card-row {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px; }}
    .card-row:last-child {{ margin-bottom: 0; }}
    .label {{ color: #64748b; font-weight: 500; }}
    .value {{ color: #0f172a; font-weight: 600; text-align: right; }}
    .btn {{ display: inline-block; background-color: #2563eb; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 16px; text-align: center; }}
    .footer {{ background: #f1f5f9; padding: 20px 24px; font-size: 13px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Prestige Realty</h1>
      <p>Site Visit Confirmation</p>
    </div>
    <div class="content">
      <div class="greeting">Dear {customer_name},</div>
      <p>Thank you for scheduling a property walkthrough with Prestige Realty. Your exclusive site visit appointment has been confirmed!</p>
      
      <div class="card">
        <div class="card-row">
          <span class="label">Property / Location:</span>
          <span class="value">{property_name} ({location})</span>
        </div>
        <div class="card-row">
          <span class="label">Date:</span>
          <span class="value">{scheduled_date_str}</span>
        </div>
        <div class="card-row">
          <span class="label">Time:</span>
          <span class="value">{scheduled_time_str} (IST)</span>
        </div>
        <div class="card-row">
          <span class="label">Booking Ref:</span>
          <span class="value">{booking_ref}</span>
        </div>
        <div class="card-row">
          <span class="label">Sales Consultant:</span>
          <span class="value">{broker_name}</span>
        </div>
        <div class="card-row">
          <span class="label">Consultant Contact:</span>
          <span class="value">{broker_phone}</span>
        </div>
      </div>

      <p>Our sales advisor will meet you at the property reception. Please let us know if you need any directions or special accommodations.</p>
      
      <p style="text-align: center;">
        <a href="{resched_link}" class="btn">Reschedule or Modify Visit</a>
      </p>
    </div>
    <div class="footer">
      Prestige Realty Estates • Asia/Kolkata Timezone<br>
      For urgent assistance, reach out directly at {broker_phone}.
    </div>
  </div>
</body>
</html>"""

    async def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        property_name: str,
        location: str,
        scheduled_date_str: str,
        scheduled_time_str: str,
        booking_ref: str,
        reschedule_url: Optional[str] = None,
    ) -> bool:
        """Dispatches HTML confirmation email to the customer."""
        if not to_email or "@" not in to_email:
            logger.warning(f"Invalid recipient email '{to_email}'. Skipping confirmation email.")
            return False

        html_body = self.build_booking_email_html(
            customer_name=customer_name,
            property_name=property_name,
            location=location,
            scheduled_date_str=scheduled_date_str,
            scheduled_time_str=scheduled_time_str,
            booking_ref=booking_ref,
            reschedule_url=reschedule_url,
        )

        subject = f"Confirmed: Your Prestige Realty Site Visit ({property_name} - {scheduled_date_str})"

        # If SMTP is configured, send via SMTP
        if self.smtp_host and self.smtp_user and self.smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = self.from_email
                msg["To"] = to_email
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, [to_email], msg.as_string())

                logger.info(f"Site visit confirmation email successfully sent to {to_email} via SMTP.")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP to {to_email}: {e}")
                return False

        # Otherwise log the verified dispatch
        logger.info(
            f"Email dispatched (Mock/Simulation mode): To={to_email}, Subject='{subject}', Ref={booking_ref}"
        )
        return True


# Global singleton instance
email_service = EmailService()
