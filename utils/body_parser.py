import base64

def extract_body(msg):
    payload = msg['payload']
    parts = payload.get("parts", [])
    body = ""

    if parts:
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
    else:
        # If there's no parts, try top-level body
        data = payload.get('body', {}).get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')

    return body
