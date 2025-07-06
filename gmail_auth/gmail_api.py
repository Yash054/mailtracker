import os.path
import base64
from email import message_from_bytes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from utils.body_parser import extract_body

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 🔄 Refresh token if needed (no browser!)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # ❌ If still not valid (e.g. missing file or refresh_token), fail
    if not creds or not creds.valid:
        raise RuntimeError("❌ Missing or invalid Gmail token. Generate token.json manually first.")

    return build('gmail', 'v1', credentials=creds)

# def fetch_recent_emails(service, max_results=5):
#     result = service.users().messages().list(userId='me', maxResults=max_results, q="subject:apply OR job").execute()
#     messages = result.get('messages', [])
#     emails = []

#     for msg in messages:
#         msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
#         payload = msg_data['payload']
#         headers = payload.get("headers", [])
#         subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
#         date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
#         parts = payload.get("parts", [])
#         body = ""
#         if parts:
#             for part in parts:
#                 if part['mimeType'] == 'text/plain':
#                     data = part['body']['data']
#                     body = base64.urlsafe_b64decode(data).decode('utf-8')
#                     break
#         emails.append({'subject': subject, 'date': date, 'body': body})
#     return emails


def fetch_recent_emails(service, label_ids=["INBOX"], query=None, max_results=100):
    """
    Fetch emails from Gmail within the past 2 weeks using Gmail search query.
    """
    if query is None:
        # 🗓️ Get date 2 weeks ago in format YYYY/MM/DD
        two_weeks_ago = (datetime.now() - timedelta(weeks=2)).strftime("%Y/%m/%d")
        query = f"after:{two_weeks_ago}"

    results = service.users().messages().list(
        userId='me',
        labelIds=label_ids,
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    emails = []

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        
        headers = txt['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        body = extract_body(txt)

        emails.append({
            'subject': subject,
            'date': date,
            'body': body
        })

    return emails
