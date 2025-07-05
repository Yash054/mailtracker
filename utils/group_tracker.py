from datetime import datetime

def parse_date_string(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except:
        return datetime.min  # fallback if format fails

def group_applications(parsed_list):
    grouped = {}

    for item in parsed_list:
        # Skip alerts and broken entries
        if not item or item['status'] is None:
            continue
        if item['status'].lower().strip() == "not relevant":
            continue  # skip alerts

        company = (item['company'] or "").lower().strip()
        job_id = (item['job_id'] or "no-id").lower().strip()
        key = (company, job_id)

        current_date = parse_date_string(item.get("date", ""))
        old_entry = grouped.get(key)

        # Save latest entry only
        if old_entry is None or current_date > parse_date_string(old_entry.get("date", "")):
            grouped[key] = item

    return list(grouped.values())
