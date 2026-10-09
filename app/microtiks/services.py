from __future__ import annotations
from typing import TYPE_CHECKING
from app.microtiks.models import Microtik,Profil, MicrotikOwner,RouteurType
from app.users.models import User
from ninja.errors import HttpError
from http import HTTPStatus
from app.microtiks.schemas import ProfilDuratinEnum
from app.utils.def_utils import connect_microtik, profil_duration,parse_mikrotik_rate
from django.db import transaction
import secrets
from app.permissions.models import PermissionGroup, Permissions
from app.microtiks.utils import PermissionGroupEnum
from app.commone.email import send_mail_creation
from config import settings
from app.microtiks.tasks import provision_gdms_task
from app.microtiks.gms import gdms_service

if TYPE_CHECKING:
    from app.subscriptions.models import SubscriptionWG


#--------------------- Le Microtik ---------------------------#

def create_microtik_service(data:dict[str,str|int], user:User) -> Microtik:
    from app.subscriptions.models import SubscriptionWG
    
    microtik = Microtik.objects.create(**data)
    SubscriptionWG.objects.create(microtik=microtik)
    group = PermissionGroup.objects.filter(slug=PermissionGroupEnum.PROPRIETAIRE_MICROTIK.value).first()
    microtik_owner = MicrotikOwner.objects.create(
        microtik=microtik, 
        user=user
        )
    
    if group:
        perms = [p for p in group.permissions.all()]
        microtik_owner.permissions.set(perms)
    return microtik


def update_microtik_service(microtik:Microtik,data:dict[str,str|int], user:User) -> Microtik:

    for key,value in data.items():
        setattr(microtik, key,value)
    microtik.save()
    
    return microtik


def retrieve_microtik_service(microtik_slug, user):
    ...


def updateInfosSubscriptionWg(data, microtik:Microtik) -> SubscriptionWG:
    device_type = microtik.device_type
    sub = microtik.subscriptionwg
    address1 = data.get('username_routeur')
    address2 = data.get('password_routeur')

    if device_type == RouteurType.GDMS:
        sub.mac_address = address1
        sub.serial_number = address2
        provision_gdms_task.delay(
            network_name= microtik.name,
            mac= address1,
            ap_password= address2,
            device_name= f'device_{microtik.name}',
            ssid_name=microtik.name.replace(' ','-'),
            subwg_slug = sub.slug
        )
    else:
        sub.mikrotik_username = address1
        sub.mikrotik_password = address2
        sub.device_name = microtik.name.replace(' ','-')
    sub.save()

    return sub


async def check_connexion(microtik: Microtik) -> dict:
    subscription = microtik.subscriptionwg

    if microtik.device_type == RouteurType.GDMS:
        network_id = subscription.gdms_network_id
        if not network_id:
            raise HttpError(
                status_code=404,
                message="veillez remplir les infos avant le test."
            )
        
        check = await gdms_service.list_voucher(
            network_id = network_id ,
            page_num=1,
            page_size=10
        )
        if not check:
            return {"status": "failled", "message": 'connexion echouer'}

        return {"status": "success", "message": "Connexion établie avec succès."}
    


#----------------------OWNER MICROTIK----------------------------------

def create_owner_service(microtik:Microtik,owner_data:dict) -> MicrotikOwner:
    email = owner_data.get("email", "")
    if User.objects.filter(email=email).exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message={'Ce address email exist est deja attribuer à un user.'}
            )
    pwd = secrets.token_urlsafe(8)
    user = User.objects.create_user(**owner_data,user_type=User.OWNERMICROTIK, password=pwd)
    group = PermissionGroup.objects.filter(slug = PermissionGroupEnum.GERANT_MICROTIK.value).first()
    permis = set(perm for perm in group.permissions.all())

    microtik_owner = MicrotikOwner.objects.create(
        microtik=microtik,
        user = user
    )
    microtik_owner.permissions.add(*permis)
    username = f"{user.first_name} {user.last_name} "
    send_mail_creation(username=username, email=user.email,pwd=pwd)
    return microtik_owner



def add_owner_service(microtik:Microtik, email:str) -> MicrotikOwner:
    user = User.objects.filter(email=email).first()
    if not user:
        raise HttpError(status_code=HTTPStatus.BAD_REQUEST,
                        message="aucun utilisateur associer à ce mail."
                        )
    
    microtik_owner = MicrotikOwner.objects.create(
        microtik=microtik,
        user=user
    )
    return microtik_owner



def remove_owner_service(microtik:Microtik, slug:str) -> dict:
    user = User.objects.filter(slug=slug).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun utilisateur associer à ce slug."
        )
    MicrotikOwner.objects.filter(
        microtik=microtik,
        user=user
    ).first().delete()

    return {"status":"success","message":"La suppression effectuer avec success."}


def add_owner_group_service(microtik:Microtik, slug_user:str, slug_group:str) -> MicrotikOwner:
    user = User.objects.filter(slug=slug_user).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun utilisateur attribuer a ce slug.'
        )

    group = PermissionGroup.objects.filter(slug=slug_group).first()
    if not group:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun groupe de permissions trouvé avec ce slug.'
        )
    
    permissions = group.permissions.all()

    microtik_owner = MicrotikOwner.objects.filter(
        microtik=microtik,
        user=user
    ).first()

    microtik_owner.permissions.add(*permissions)
    return {"status":"success", "message":"Utilisateur ajouter dans le group avec success."}



def remove_owner_group_service(microtik:Microtik, slug:str, slug_group:str) -> MicrotikOwner:
    """Retirer les permission d'un gestionnaire"""

    user = User.objects.filter(slug=slug).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun utilisateur attribuer a ce slug.'
        )

    group = PermissionGroup.objects.filter(slug=slug_group).first()
    if not group:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun groupe de permissions trouvé avec ce slug.'
        )
    
    slug_permissions = group.permissions.values_list('slug')

    microtik_owner = MicrotikOwner.objects.filter(
        microtik=microtik,
        user=user
    ).first()

    resist_perms = microtik_owner.permissions.exclude(slug__in=slug_permissions)
    microtik_owner.permissions.set(*resist_perms)
    return {"status":"success", "message":"Utilisateur ajouter dans le group avec success."}



#-------------- Profil ------------------------#

def create_profil_service(data: dict, microtik: Microtik) -> dict:
    wg = microtik.subscriptionwg

    type_session = data.pop('type_session', 'h')
    duration = data.pop('duration', 1)
    session_timeout,session_timeout_dict = profil_duration(duration=duration, type_session=type_session)
    price = data.get("price", 0.00)
    
    profile_name = data.get("name", "default_profil")
    rate_limit = data.get("rate_limit", "512k/1M")
    shared_users = str(data.get("shared_users", 1))
    up_rate, down_rate = parse_mikrotik_rate(rate_limit)

    Profil.objects.create(
        name=profile_name,
        rate_limit=rate_limit,
        shared_users=int(shared_users),
        session_timeout=session_timeout,
        session_timeout_dict = session_timeout_dict,
        price=price,
        microtik=microtik,
        up_rate= up_rate,
        down_rate = down_rate
    )
        
    return {"status": "success", "message": "Profil créé avec succès sur le routeur "}
        



def update_profil_service(microtik: Microtik, slug_profil: str, data: dict) -> dict:
    wg = microtik.subscriptionwg

    profil = microtik.profils.filter(slug=slug_profil).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant à ce slug."
        )
    
    type_session = data.pop('type_session', '')
    duration = data.pop('duration', '')
    
    session_timeout,session_timeout_dict = None,None
    if type_session and duration:
        session_timeout,session_timeout_dict = profil_duration(duration=duration, type_session=type_session)
        data['session_timeout'] = session_timeout
        data['session_timeout_dict'] = session_timeout_dict
        
    rate_limit = data.get('rate_limit','')
    if rate_limit:
        up_rate, down_rate = parse_mikrotik_rate(rate_limit)
        data['up_rate'] = up_rate
        data['down_rate'] = down_rate

    for key, value in data.items():
        if hasattr(profil, key):  
            setattr(profil, key, value)
    profil.save()

    return {"status": "success", "message": "Profil modifié avec succès."}


def delete_profil_service(microtik: Microtik, profil_slug: str) -> dict:
    wg = microtik.subscriptionwg

    profil = microtik.profils.filter(slug=profil_slug).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant à ce slug."
        )
    
    profil.is_active = False
    profil.save(update_fields=['is_active'])
        
    return {"status": "success", "message": "Profil supprimé avec succès."}
        


def profil_liste_service(microtik_slug:str):
    microtik = Microtik.objects.filter(slug=microtik_slug).first()
    
    profil = microtik.profils.all()

    return profil



