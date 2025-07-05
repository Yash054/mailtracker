from gmail_auth.gmail_api import authenticate_gmail, fetch_recent_emails
from ai_parser.email_parser import parse_email
from ai_parser.data_cleaner import clean_parsed_output
from utils.group_tracker import group_applications
from db.supabase_client import supabase
from datetime import datetime, timedelta


def clean_old_records():
    """🧹 Delete entries older than 2 weeks from Supabase DB"""
    cutoff_date = (datetime.utcnow() - timedelta(days=14)).isoformat() + 'Z'
    supabase.table("MailTracker").delete().lt("email_date", cutoff_date).execute()


def upsert_to_supabase(applications):
    """
    🔁 Insert new entries or update if same (company_name + job_id) already exists.
    If job_id is missing, treat as new entry.
    """
    for app in applications:
        company = app.get("company")
        job_id = app.get("job_id")

        # If job_id is missing, treat as new unique entry every time
        if not job_id:
            supabase.table("MailTracker").insert({
                "company_name": company,
                "role": app.get("role"),
                "job_id": None,
                "status": app.get("status"),
                "summary": app.get("summary"),
                "email_date": app.get("date")
            }).execute()
        else:
            # Check if entry with same company and job_id exists
            existing = supabase.table("MailTracker").select("*").eq("company_name", company).eq("job_id", job_id).execute()
            if existing.data:
                supabase.table("MailTracker").update({
                    "status": app.get("status"),
                    "summary": app.get("summary"),
                    "email_date": app.get("date")
                }).eq("company_name", company).eq("job_id", job_id).execute()
            else:
                supabase.table("MailTracker").insert({
                    "company_name": company,
                    "role": app.get("role"),
                    "job_id": job_id,
                    "status": app.get("status"),
                    "summary": app.get("summary"),
                    "email_date": app.get("date")
                }).execute()


def main():
    print("📬 Connecting to Gmail...")
    service = authenticate_gmail()
    raw_emails = fetch_recent_emails(service)

    print(f"📨 {len(raw_emails)} emails fetched.")
    parsed_apps = []

    for email in raw_emails:
        try:
            parsed_text = parse_email(email['subject'], email['body'])
            cleaned = clean_parsed_output(parsed_text)
            cleaned['date'] = datetime.strptime(email['date'], "%a, %d %b %Y %H:%M:%S %z").astimezone().isoformat()
            parsed_apps.append(cleaned)
        except Exception as e:
            print(f"❌ Error parsing email: {e}")
            continue

    print(f"📊 Parsed {len(parsed_apps)} applications")
    grouped = group_applications(parsed_apps)
    print(f"✅ {len(grouped)} final entries after grouping")

    clean_old_records()
    upsert_to_supabase(grouped)
    print("✅ DB Updated")


if __name__ == "__main__":
    main()
