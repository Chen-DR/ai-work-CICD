DANGEROUS_CHARS = [";", "&&", "|", "`", "$(", ">", "<", "\n", "\r"]


def sanitize_param(value: str) -> str:
    """Remove dangerous characters from a parameter value."""
    result = value
    for c in DANGEROUS_CHARS:
        result = result.replace(c, "")
    return result


def validate_param(value: str) -> bool:
    """Check if a parameter value contains dangerous characters."""
    return not any(c in value for c in DANGEROUS_CHARS)
