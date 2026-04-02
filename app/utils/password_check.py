def check_security_password(password: str):
    if len(password) < 5:
        return {
            "status": False,
            "message": "The password must contain at least 5 characters.",
        }

    if not (
        any(char.isdigit() for char in password)
        and any(char.isalpha() for char in password)
        and any(char.islower() for char in password)
        and any(char.isupper() for char in password)
    ):
        return {
            "status": False,
            "message": "The password must contain at least one uppercase letter, one lowercase letter, and one digit.",
        }

    return {"status": True, "message": "The password is valid."}
