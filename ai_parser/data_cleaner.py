# ai_parser/data_cleaner.py

def clean_parsed_output(parsed_text):
    """Convert raw parsed output into a dict with clean fields"""
    import re

    def extract(key, block):
        pattern = rf"{key}:\s*(.*)"
        match = re.search(pattern, block)
        return match.group(1).strip() if match else None

    return {
        "company": extract("Company Name", parsed_text),
        "role": extract("Role/Position", parsed_text),
        "job_id": extract("Job ID", parsed_text),
        "status": extract("Application Status", parsed_text),
        "action": extract("Action Required", parsed_text),
        "update": extract("Is this email an update to a previous application?", parsed_text),
        "summary": extract("Short Summary", parsed_text),
    }
