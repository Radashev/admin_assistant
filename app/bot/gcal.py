import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None
    token_path = "token.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def add_event_to_gcal(summary: str, start_dt: datetime.datetime):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Warsaw"},
        "end": {
            "dateTime": (start_dt + datetime.timedelta(hours=1)).isoformat(),
            "timeZone": "Europe/Warsaw",
        },
    }

    event_result = service.events().insert(calendarId="primary", body=event).execute()
    return event_result.get("htmlLink")
