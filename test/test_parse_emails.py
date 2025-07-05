from gmail_auth.gmail_api import authenticate_gmail, fetch_recent_emails
from ai_parser.email_parser import parse_email
from ai_parser.data_cleaner import clean_parsed_output
from utils.group_tracker import group_applications

if __name__ == "__main__":
    service = authenticate_gmail()
    emails = fetch_recent_emails(service)

    parsed = []

    for i, email in enumerate(emails):
        print(f"\n🔍 Parsing Email {i+1}")
        print("Subject:", email['subject'])
        print("Date:", email['date'])

        ai_response = parse_email(email['subject'], email['body'])
        structured = clean_parsed_output(ai_response)
        structured['subject'] = email['subject']
        structured['date'] = email['date']
        parsed.append(structured)

    grouped = group_applications(parsed)

    print("\n🗂️ Final Applications Tracked:")
    for app in grouped:
        print(f"\n✅ {app['company']} | {app['role']} | {app['job_id']}")
        print("📅", app['date'])
        print("📌 Status:", app['status'])
        print("📝", app['summary'])
