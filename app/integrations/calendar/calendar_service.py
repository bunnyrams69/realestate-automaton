"""
Calendar Integration Service
Supports universal RFC 5545 iCalendar (.ics) generation, Google Calendar one-click add links,
and optional Google Calendar API synchronization via service accounts.
"""

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Dict, Optional
import urllib.parse
from app.config.settings import settings
from app.core.logging import logger


class CalendarService:
    """Service for generating calendar invites and synchronizing site visits."""

    @staticmethod
    def generate_google_calendar_link(
        title: str,
        start_time: datetime,
        duration_minutes: int,
        description: str,
        location: str,
    ) -> str:
        """
        Generate a direct, zero-auth Google Calendar 'Add to Calendar' URL.
        Clicking this link on mobile or desktop pre-fills Google Calendar instantly.
        """
        # Format dates as YYYYMMDDTHHMMSSZ
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        start_str = start_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        end_str = end_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        params = {
            "action": "TEMPLATE",
            "text": title,
            "dates": f"{start_str}/{end_str}",
            "details": description,
            "location": location,
        }
        return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"

    @staticmethod
    def generate_ics_content(
        uid: str,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        description: str,
        location: str,
        organizer_name: str = "Prestige Realty Estates",
        organizer_email: str = "visits@prestigerealty.com",
    ) -> str:
        """
        Generate standard RFC 5545 iCalendar (.ics) file string.
        Compatible with Apple Calendar, Outlook, and Google Calendar.
        """
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        end_time = start_time + timedelta(minutes=duration_minutes)
        dtstart = start_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dtend = end_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        # Escape special characters per RFC 5545
        clean_desc = description.replace("\n", "\\n").replace(",", "\\,")
        clean_loc = location.replace("\n", " ").replace(",", "\\,")
        clean_title = title.replace("\n", " ").replace(",", "\\,")

        return (
            "BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//Real Estate AI Automation//Site Visit Scheduler//EN\r\n"
            "CALSCALE:GREGORIAN\r\n"
            "METHOD:REQUEST\r\n"
            "BEGIN:VEVENT\r\n"
            f"UID:{uid}@prestigerealty.com\r\n"
            f"DTSTAMP:{dtstamp}\r\n"
            f"DTSTART:{dtstart}\r\n"
            f"DTEND:{dtend}\r\n"
            f"SUMMARY:{clean_title}\r\n"
            f"DESCRIPTION:{clean_desc}\r\n"
            f"LOCATION:{clean_loc}\r\n"
            f"ORGANIZER;CN={organizer_name}:mailto:{organizer_email}\r\n"
            "STATUS:CONFIRMED\r\n"
            "BEGIN:VALARM\r\n"
            "TRIGGER:-PT2H\r\n"
            "ACTION:DISPLAY\r\n"
            "DESCRIPTION:Reminder: Real estate site visit in 2 hours\r\n"
            "END:VALARM\r\n"
            "END:VEVENT\r\n"
            "END:VCALENDAR\r\n"
        )

    async def create_google_calendar_event(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        description: str,
        location: str,
        attendee_email: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create event via Google Calendar Service Account API if configured on disk.
        Returns the external Google Calendar Event ID, or None if service account is not active.
        """
        cred_path = settings.GOOGLE_CALENDAR_CREDENTIALS_FILE
        if not os.path.exists(cred_path):
            logger.info("Google Calendar service account file not found. Falling back to link generator.")
            return None

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds = service_account.Credentials.from_service_account_file(
                cred_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            service = build("calendar", "v3", credentials=creds)

            end_time = start_time + timedelta(minutes=duration_minutes)
            event_body = {
                "summary": title,
                "location": location,
                "description": description,
                "start": {"dateTime": start_time.isoformat()},
                "end": {"dateTime": end_time.isoformat()},
            }
            if attendee_email:
                event_body["attendees"] = [{"email": attendee_email}]

            created = (
                service.events()
                .insert(calendarId=settings.GOOGLE_CALENDAR_ID, body=event_body)
                .execute()
            )
            event_id = created.get("id")
            logger.info(f"Google Calendar event created successfully with ID: {event_id}")
            return event_id

        except Exception as e:
            logger.warning(f"Failed to create Google Calendar API event: {e}. Fallback link is ready.")
            return None


calendar_service = CalendarService()
