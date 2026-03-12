import json
import os

MAX_BODY_LOG_SIZE = int(os.getenv('MAX_BODY_LOG_SIZE', 1_048_576))  # default 1 MB


def format_body(body: bytes) -> dict | str:
    if len(body) > MAX_BODY_LOG_SIZE:
        return f'<body too large: {len(body) / 1_048_576:.1f}MB>'
    try:
        decoded = body.decode('utf-8')
    except UnicodeDecodeError:
        return '<binary data>'

    try:
        return json.loads(decoded)
    except (json.JSONDecodeError, ValueError):
        return decoded
