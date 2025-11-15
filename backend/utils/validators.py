def validate_email(email: str) -> bool:
    return "@" in email and "." in email

def validate_required(value) -> bool:
    return value is not None and value != ""
