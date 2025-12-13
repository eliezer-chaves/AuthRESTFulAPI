def mask_email(email: str) -> str:
    name, domain = email.split("@")
    
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[:2] + "*" * (len(name) - 2)
    
    return f"{masked_name}@{domain}"
