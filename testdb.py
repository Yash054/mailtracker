from db.supabase_client import supabase

# After you get parsed values like company_name, role, etc.
supabase.table("MailTracker").insert({
    "company_name": "Quest Global",
    "role": "Java Developer",
    "job_id": "P-109581",
    "status": "Applied",
    "summary": "Thanked for application",
    "email_date": "2025-07-04T03:33:24Z"
}).execute()