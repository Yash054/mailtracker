import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmail_auth.gmail_api import authenticate_gmail, fetch_recent_emails

service = authenticate_gmail()
emails = fetch_recent_emails(service)

for i, mail in enumerate(emails):
    print(f"\n📧 Email {i+1}")
    print("Subject:", mail['subject'])
    print("Date:", mail['date'])
    print("Body:", mail['body'][:200], "...\n")
