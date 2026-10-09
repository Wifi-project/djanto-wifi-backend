import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
import django
from django.conf import settings

django.setup()

from django.core.mail import send_mail

print("=== Configuration email ===")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_TIMEOUT: {settings.EMAIL_TIMEOUT}")

print("\n=== Test envoi email ===")
try:
    result = send_mail(
        subject="Test email",
        message="Ceci est un test.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["fode.dounoh.5@gmail.com"],
        fail_silently=False,
    )
    print(f"SUCCESS: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")