from app.commone.tasks import send_async_email_task, sender_email
import os

def send_mail_creation(username: str, email: str, pwd: str, activation_token: str):
    # Construction du lien d'activation complet (ex: https://tondomaine.com/api/profile/users/activate/?token=...)
    activation_link = f"{os.getenv("DJANTO_DOMAINE")}/active/{activation_token}"

    sender_email(
        subject="Création de votre compte - Bienvenue sur Djanto wifi",
        message=(
            f"Bonjour {username},\n\n"
            f"Nous avons le plaisir de vous informer que votre compte a été créé avec succès sur notre plateforme.\n\n"
            f"Vos informations de connexion :\n"
            f"   • Email : {email}\n"
            f"   • Mot de passe temporaire : {pwd}\n\n"
            f"Veuillez activer votre compte en cliquant sur le lien ci-dessous :\n"
            f"🔗 {activation_link}\n\n"
            f"⚠️ Ce lien est valable pendant 24 heures.\n\n"
            f"   • Ne partagez jamais vos identifiants\n\n"
            f"Cordialement,\n"
            f"L'équipe Djanto wifi"
        ),
        recipient_list=[email],
    )


def send_mail_password_update(username: str, email: str, new_pwd: str):
    sender_email(
        subject="Modification de votre mot de passe - Djanto wifi",
        message=(
            f"Bonjour {username},\n\n"
            f"Nous vous informons que votre mot de passe a été modifié avec succès.\n\n"
            f"Vos nouveaux identifiants de connexion :\n"
            f"   • Email : {email}\n"
            f"   • Nouveau mot de passe : {new_pwd}\n\n"
            f"⚠️  IMPORTANT : Si vous n'êtes pas à l'origine de cette modification, veuillez contacter immédiatement l'administrateur de la plateforme.\n\n"
            f"Cordialement,\n"
            f"L'équipe Djanto wifi"
        ),
        recipient_list=[email],
    )


def send_password_reset_mail(username: str, email: str, reset_token: str):
    # Lien pointant vers ton front ou ton API de réinitialisation (ex: /reset-password?token=...)
    reset_link = f"{os.getenv("DJANTO_DOMAINE")}/password/reset/{reset_token}/"

    sender_email(
        subject="Réinitialisation de votre mot de passe - Djanto wifi",
        message=(
            f"Bonjour {username},\n\n"
            f"Vous avez demandé la réinitialisation de votre mot de passe sur Djanto wifi.\n\n"
            f"Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :\n"
            f"🔗 {reset_link}\n\n"
            f"⚠️ Ce lien est valable pendant **2 heures** uniquement.\n"
            f"Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail.\n\n"
            f"Cordialement,\n"
            f"L'équipe Djanto wifi"
        ),
        recipient_list=[email],
    )