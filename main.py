from gmail_auth.gmail_api import authenticate_gmail, fetch_recent_emails
from ai_parser.email_parser import parse_email
from ai_parser.data_cleaner import clean_parsed_output
from utils.group_tracker import group_applications
from db.supabase_client import supabase
from datetime import datetime, timedelta
from dateutil import parser


def clean_old_records():
    """ Delete entries older than 2 weeks from Supabase DB"""
    cutoff_date = (datetime.utcnow() - timedelta(days=21)).isoformat() + 'Z'
    supabase.table("MailTracker").delete().lt("email_date", cutoff_date).execute()


def upsert_to_supabase(applications):
    """
    Insert new entries or update if same (company_name + job_id) already exists.
    If job_id is missing, treat as new entry.
    Avoid inserting duplicates by checking (company_name + email_date).
    """
    for app in applications:
        company = (app.get("company") or "").strip().lower()
        job_id = app.get("job_id")
        email_date = app.get("date")

        # ✅ Skip if exact same email already exists
        existing_email = supabase.table("MailTracker").select("*").eq("company_name", company).eq("email_date", email_date).execute()
        if existing_email.data:
            print(f"Skipping duplicate: {company} - {email_date}")
            continue

        # 🔁 If job_id exists, update if already present
        if job_id:
            existing = supabase.table("MailTracker").select("*").eq("company_name", company).eq("job_id", job_id).execute()
            if existing.data:
                supabase.table("MailTracker").update({
                    "status": app.get("status"),
                    "summary": app.get("summary"),
                    "email_date": email_date
                }).eq("company_name", company).eq("job_id", job_id).execute()
                print(f"Updated: {company} - {job_id}")
            else:
                supabase.table("MailTracker").insert({
                    "company_name": company,
                    "role": app.get("role"),
                    "job_id": job_id,
                    "status": app.get("status"),
                    "summary": app.get("summary"),
                    "email_date": email_date
                }).execute()
                print(f"Inserted new with job ID: {company} - {job_id}")
        else:
            # If no job_id, insert as a fresh entry (already passed duplicate check)
            supabase.table("MailTracker").insert({
                "company_name": company,
                "role": app.get("role"),
                "job_id": None,
                "status": app.get("status"),
                "summary": app.get("summary"),
                "email_date": email_date
            }).execute()
            print(f"Inserted new without job ID: {company} - {email_date}")



def main():
    print("Connecting to Gmail...")
    service = authenticate_gmail()
    raw_emails = fetch_recent_emails(service, max_results=10)

    print(f"{len(raw_emails)} emails fetched.")
    parsed_apps = []

    for email in raw_emails:
        try:
            parsed_text = parse_email(email['subject'], email['body'])
            cleaned = clean_parsed_output(parsed_text)
            cleaned['date'] = parser.parse(email['date']).astimezone().isoformat()
            parsed_apps.append(cleaned)
        except Exception as e:
            print(f"Error parsing email: {e}")
            continue

    print(f"Parsed {len(parsed_apps)} applications")
    grouped = group_applications(parsed_apps)
    print(f"{len(grouped)} final entries after grouping")

    clean_old_records()
    upsert_to_supabase(grouped)
    print("DB Updated")


if __name__ == "__main__":
    main()
