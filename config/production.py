import os

RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")

ALLOWED_HOSTS = [
    "djanto-web.onrender.com",
    RENDER_HOSTNAME,
]

CSRF_TRUSTED_ORIGINS = [
    f"https://{RENDER_HOSTNAME}",
] if RENDER_HOSTNAME else []