from ninja import Router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja.pagination import paginate, LimitOffsetPagination 
from app.users.models import User
from typing import List
from http import HTTPStatus
from ninja.errors import HttpError
from app.users.schemas import UserInSchema,UserOutSchema, UserUpdate, UserPasswordUpdate, UserPasswordUpdateMe
from app.users.services import user_creation, update_user as update_user_service, reset_password
from app.users.deps import GlobalAuth
from django.contrib.auth.hashers import check_password
from app.utils.password_check import check_security_password

user_router = Router(tags=['Users'])

@user_router.get('/me', response=UserOutSchema,auth=[GlobalAuth()])
def get_current_user(request):
    user_id = request.user
    return user_id


@user_router.patch('/me', response=UserOutSchema, auth=GlobalAuth())
def update_current_user(request, user_info:UserUpdate) -> UserOutSchema:
    user = request.user

    return update_user_service(
        user=user, 
        data=user_info.model_dump(exclude_unset=True)
        )


@user_router.post('/me/reset_password/', auth=GlobalAuth())
def current_user_reset_password(request,data:UserPasswordUpdateMe) -> dict[int,str]:
    user = request.user

    if not check_password(data.password, user.password):
        raise HttpError(400, "L'ancien mot de passe est incorrect")

    if data.password == data.new_password:
        raise HttpError(400, "Le nouveau mot de passe doit être différent de l'ancien")

    reset_password(user=user,password=data.new_password)
    return {200:"Mot de pass modifier avec success"}

    

@user_router.delete('/me/delete/', auth=GlobalAuth())
def current_user_delete(request):
    user = request.user
    user.delete()
    return {'message':"Compte supprimer avec success"}


@user_router.get('/profile/users', response=List[UserOutSchema], auth=GlobalAuth([]))  
@paginate(LimitOffsetPagination, page_size=10)  
def user_list(request):
    return User.objects.all()


@user_router.post('/profile/users/', response=UserOutSchema)
def create_user(request,user:UserInSchema) -> UserOutSchema:
    return user_creation(data=user.model_dump())


@user_router.patch('profile/users/{slug}',response=UserOutSchema, auth=GlobalAuth([]))
def update_user(request,slug,data:UserUpdate)-> UserOutSchema:
    return update_user_service(
                slug=slug,
                data=data.model_dump(exclude_unset=True)
                )

@user_router.post('profile/users/reset_password/',auth=GlobalAuth([]))
def user_reset_password(request,data:UserPasswordUpdate) -> dict[int,str]:
    password = data.new_password
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(
            status_code=404,
            message="Aucun utilisateur trouver avec ce mail"
        )
    check_pass = check_security_password(password=password)
    if check_pass['status'] is False:
        return check_pass
    
    reset_password(user=user,password=password)

    return {200:"Le mot de passe modifier avec success.\n Veillez consulter votre mail."}


@user_router.delete('profile/users/{slug}/',auth=GlobalAuth([]))
def delete_user(request,slug):
    try:
        user = User.objects.get(slug=slug)
    except Exception as e:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Utilisateur avec ce slug nexiste pas"
        )
    user.delete()

    return {'message':"Utilisateur supprimer avec success."}

