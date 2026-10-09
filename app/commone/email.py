from app.commone.tasks import send_async_email_task


def send_mail_creation(username:str, email:str,pwd:str):
    send_async_email_task.delay(
    subject="Création de votre compte - Bienvenue sur Djanto wifi",
    message=(
        f"Bonjour {username},\n\n"
        f"Nous avons le plaisir de vous informer que votre compte a été créé avec succès sur notre plateforme.\n\n"
        f"Vos informations de connexion :\n"
        f"   • Email : {email}\n"
        f"   • Mot de passe temporaire : {pwd}\n\n"
        f"⚠️  IMPORTANT : Pour des raisons de sécurité, vous devez changer votre mot de passe lors de votre première connexion.\n\n"
        f"   • Ne partagez jamais vos identifiants\n\n"
        f"Cordialement,\n"
        f"L'équipe Djanto wifi"
    ),
    recipient_list=[email],
)
