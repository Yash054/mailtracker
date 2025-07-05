from db.supabase_client import supabase
from datetime import datetime, timedelta

# ⏳ Keep data only for the last 2 weeks
def cleanup_old_entries():
    cutoff_date = (datetime.utcnow() - timedelta(weeks=2)).isoformat() + 'Z'
    supabase.table("MailTracker").delete().lt("email_date", cutoff_date).execute()

# 🚀 Add or update application entry
def store_application(entry):
    cleanup_old_entries()

    company = entry.get("company_name")
    job_id = entry.get("job_id")

    # Try to find existing application
    match_query = supabase.table("MailTracker")

    if job_id and job_id != "Not mentioned" and job_id != "N/A":
        match_query = match_query.eq("company_name", company).eq("job_id", job_id)
    else:
        match_query = match_query.eq("company_name", company).is_("job_id", None)

    result = match_query.execute()
    data = result.data

    if data and len(data) > 0:
        # 📝 Update existing record (keep latest date and new status/summary)
        record_id = data[0]["id"]  # assuming table has "id" column
        supabase.table("MailTracker").update({
            "status": entry["status"],
            "summary": entry["summary"],
            "email_date": entry["email_date"]
        }).eq("id", record_id).execute()
    else:
        # ➕ Insert new record
        supabase.table("MailTracker").insert(entry).execute()
