import string
import secrets
from app.users.models import User
from ninja.errors import HttpError
from django.contrib.auth.hashers import make_password
from app.utils.password_check import check_security_password


def user_creation(data:dict=[str,str | bool] ):
    if User.objects.filter(email=data['email']).exists():
        raise HttpError(
            status_code=404,
            message="Un utilisateur avec ce mail exist"
        )
    password=data.pop('password')
    result = check_security_password(password=password)

    if result['status'] is False:
        return result
    
    user = User.objects.create_user(
        **data,
        password=password
    )
    return user


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
    
    return True


