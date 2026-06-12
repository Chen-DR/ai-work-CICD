import re

SENSITIVE_PATTERNS = [
    (r"password\s*[:=]\s*\S+", "password=******"),
    (r"secret\s*[:=]\s*\S+", "secret=******"),
    (r"api_key\s*[:=]\s*\S+", "api_key=******"),
    (r"Authorization:\s*Bearer\s+\S+", "Authorization: Bearer ******"),
    (r"sk-[a-zA-Z0-9]{20,}", "sk-******"),
]


def mask_sensitive(text: str) -> str:
    """Mask sensitive data in log output."""
    result = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result
