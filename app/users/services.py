import string
import secrets
from app.users.models import User
from ninja.errors import HttpError
from django.contrib.auth.hashers import make_password
from app.utils.password_check import check_security_password
from app.commone.email import (
    send_mail_creation,
    send_mail_password_update,
    send_password_reset_mail,
    )
from urllib.parse import unquote
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired



def user_creation(data:dict=[str,str | bool] ):
    from app.permissions.models import PermissionGroup
    from app.gdms.utils import PermissionGroupEnum

    type_user = data.get('user_type','')

    if User.objects.filter(email=data['email']).exists():
        raise HttpError(
            status_code=404,
            message="Un utilisateur avec ce mail exist"
        )

    result = {}
    password=data.pop('password')
    if password:
        result = check_security_password(password=password)
    else:
        password = secrets.token_urlsafe(9)

    if result.get("status") is False:
        return result
    
    user = User.objects.create_user(
        **data,
        password=password,
        is_active=False
    )

    group = None
    if type_user == User.OWNERMICROTIK:
        group = PermissionGroup.objects.filter(slug=PermissionGroupEnum.INIT_PROPRIETAIRE_NETWORK.value).first()
    if type_user == User.ADMIN:
        group = PermissionGroup.objects.filter(slug = PermissionGroupEnum.ADMINISTRATION.value).first()

    if group:
        group.users.add(user)
        username = f'{user.first_name} {user.last_name}'

    signer = TimestampSigner()
    token = signer.sign(user.email)
    

    send_mail_creation(username=username,email=user.email,pwd=password,activation_token=token)
    return user


def user_activation_service(token):
    token = unquote(token)
    signer = TimestampSigner()

    try:
        email = signer.unsign(token, max_age=86400)
    except SignatureExpired:
        raise HttpError(400, "Le lien d'activation a expiré. Veuillez demander un nouveau lien.")
    except BadSignature:
        raise HttpError(400, "Token d'activation invalide.")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise HttpError(400, "Utilisateur introuvable.")

    if user.is_active:
        raise HttpError(400, "Ce compte est déjà activé.")

    user.is_active = True
    user.save(update_fields=['is_active'])

    return {"status": "success", "message": "Compte activé avec succès !"}



def forgot_password_service(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return {"status": "success", "message": "Un lien de réinitialisation a été envoyé."}

    signer = TimestampSigner()
    reset_token = signer.sign(user.email)

    username = f"{user.first_name} {user.last_name}".strip() or "Utilisateur"

    send_password_reset_mail(
        username=username,
        email=user.email,
        reset_token=reset_token
    )

    return {"status": "success", "message": "Un lien de réinitialisation a été envoyé."}



def set_new_password(token,new_password1,new_password2):
    signer = TimestampSigner()
    
    try:
        email = signer.unsign(token, max_age=7200)
    except SignatureExpired:
        raise HttpError(400, "Le lien de réinitialisation a expiré (valable 2 heures). Veuillez refaire une demande.")
    except BadSignature:
        raise HttpError(400, "Token de réinitialisation invalide.")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise HttpError(404, "Utilisateur introuvable.")

    if new_password1 != new_password2:
        raise HttpError(
            status_code=404,
            message="les mots de passes ne se correspondent pas."
        )

    security_check = check_security_password(password=new_password1)
    if security_check.get("status") is False:
        return security_check

    user.set_password(new_password1)
    user.is_active = True
    user.save()

    return {"status": "success", "message": "Votre mot de passe a été réinitialisé avec succès !"}



def update_user_service(user:User,data:dict=[str,str | bool]):
    
    for attr, value in data.items():
        setattr(user, attr, value)
    user.save()

    return user


def retrive_user_service(slug:str):
    user = User.objects.filter(slug=slug).first()

    if not user:
        raise HttpError(
            status_code=404,
            message="Aucun utilisateur correspondant à ce slug."
        )
    
    return user



def reset_password(user:User,password:str):
    # try:
    #     user = User.objects.get(slug=slug)
    # except User.DoesNotExist:
    #     return HttpError(
    #         status_code=400,
    #         message="Aucun utilisateur existant pour ce slug."
    #     )
    user.password=make_password(password)
    user.save()
    username = f'{user.first_name} {user.last_name}'

    send_mail_password_update(username=username, email=user.email,new_pwd=password)
    
    return True


