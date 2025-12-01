"""
Google Calendar API integration for creating meetings with Google Meet links.
"""
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def create_google_meet_event(counselling_email, studying_email, scheduled_time, duration_minutes=30):
    """
    Create a Google Calendar event with Google Meet link.
    
    Args:
        counselling_email: Email of counselling student
        studying_email: Email of studying student
        scheduled_time: datetime object for meeting time
        duration_minutes: Duration in minutes (default 30)
    
    Returns:
        dict with 'meet_link' and 'event_id' or None if error
    """
    try:
        credentials_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        calendar_email = settings.GOOGLE_CALENDAR_EMAIL
        
        if not credentials_path or not os.path.exists(credentials_path):
            logger.error("Google Calendar credentials file not found")
            return None
        
        if not calendar_email:
            logger.error("GOOGLE_CALENDAR_EMAIL not configured")
            return None
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Delegate to the calendar email
        delegated_credentials = credentials.with_subject(calendar_email)
        
        # Build service
        service = build('calendar', 'v3', credentials=delegated_credentials)
        
        # Calculate end time
        end_time = scheduled_time + timedelta(minutes=duration_minutes)
        
        # Create event
        event = {
            'summary': f'KCET EduGuide: Counselling Meeting',
            'description': f'Meeting between counselling student ({counselling_email}) and studying student ({studying_email})',
            'start': {
                'dateTime': scheduled_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': counselling_email},
                {'email': studying_email},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'meet-{datetime.now().timestamp()}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 15},  # 15 minutes before
                ],
            },
        }
        
        # Insert event
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        # Extract Meet link
        meet_link = created_event.get('hangoutLink') or created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
        
        return {
            'meet_link': meet_link,
            'event_id': created_event.get('id'),
            'scheduled_time': scheduled_time,
        }
    
    except Exception as e:
        logger.error(f"Error creating Google Calendar event: {str(e)}")
        return None

