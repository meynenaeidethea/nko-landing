def validate_email(email):
    return "@" in email and "." in email

def validate_required(field):
    return field is not None and field != ""
