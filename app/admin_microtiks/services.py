from datetime import datetime, timedelta
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import InfoDeposit, Client
from typing import TYPE_CHECKING
from django.db import transaction
from app.users.models import User
from app.utils.def_utils import connect_microtik, generer_code_unique
from app.microtiks.models import Profil

from app.microtiks.models import Microtik


def creer_ticket_code(microtik,code_paye, profile_name, limit_uptime):
    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )

    api = connection.get_api()
    list_user = api.get_resource('/ip/hotspot/user')
    
    try:
        for code in code_paye:
            list_user.add(
                name=code, 
                password=code, 
                profile=profile_name,
                limit_uptime = limit_uptime,
                comment=f"Date: {datetime.fromtimestamp(timezone.now())} admin generation"
            )
        return {"status":True,"message":f"success"}
    
    except Exception as e:
        if "already exists" in str(e).lower():
            pass

        return {"status":False,"message":f"Erreur MikroTik : {e}"}
    
    finally:
        connection.disconnect()
        

def create_users(microtik_slug,profil_slug,user_numbers):
    microtik = Microtik.objects.prefetch_related("profils").filter(slug=microtik_slug).first()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspondant a ce microtik."
        )

    profil = microtik.profils.filter(slug=profil_slug)
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspondant a ce profil."
        )
    codes = [generer_code_unique() for _ in range(user_numbers)]
    
    users = creer_ticket_code(
        microtik=microtik,
        code_paye=codes,
        profile_name=profil.name,
        limit_uptime=profil.session_timeout
    )
    if users.get('status',False) is False:
        return {
            "username":"",
            "password":""
        }
    
    model_client = [Client(
        code_username = code,
        code_password = code,
        microtik = microtik,
        limit_uptime = profil.session_timeout,
        profil_name = profil.name) for code in codes]
    
    Client.objects.bulk_create(model_client)

    return [
            {
                "username":code,
                "password": code
            } for code in codes
        ]


def list_user(microtik_slug:str,owner:User) -> list[User]:
    microtik = Microtik.objects.prefetch_related("clients").filter(slug=microtik_slug,owner=owner).first()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspondant a ce microtik."
        )
    users = microtik.clients.all()
    return users


def retrieve_user(microtik_slug:str,client_slug:str,owner:User) -> User:
    client = Client.objects.select_related("microtik").filter(
        microtik__slug = microtik_slug,
        slug = client_slug
    ).first()

    if not client:
        raise HttpError(
            status_code=404,
            message="aucun client trouver pour ce slug"
        )
    return client


def blocked_unlocked_user(microtik_slug:str,user_slug:str,is_desable:bool):
    microtik = Microtik.objects.select_related("clients").filter(slug=microtik_slug).first()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="slug du microtik n'exist pas."
        )
    client = microtik.clients.filter(slug=user_slug).first()
    if not client:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="slug de ce client n'exist pas."
        )

    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    api = connection.get_api()
    list_user = api.get_resource('/ip/hotspot/user')
    users_trouves = list_user.get(name=client.code_username)

    if users_trouves:
        user_id = users_trouves[0]['.id']
        
        if is_desable is True:
            list_user.set(id=user_id, disabled='yes')

            active_resource = api.get_resource('/ip/hotspot/active')
            session_active = active_resource.get(user=client.code_username)
            if session_active:
                active_resource.remove(id=session_active[0]['.id'])

            client.status = Client.DISABLE
        else:
            list_user.set(id=user_id, disabled='no')
            client.status = Client.DISABLE

        client.status = Client.save()
        return {"status":"success", "message":"modification effectuer avec sucess"}

    else:
        return {"status":"success", "message":"slug de ce client n'exist pas sur le microtik."}


def actif_user_list(microtik_slug):
    microtik = Microtik.objects.filter(slug=microtik_slug).first()
    
    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    
    api = connection.get_api()
    active_resource = api.get_resource('/ip/hotspot/active')
    active_users = active_resource.get()

    users_list = []
    for session in active_users:
        session_timeout = int(session.get('session-timeout', 0))
        uptime = int(session.get('uptime', 0))  
        expire_in = session_timeout - uptime if session_timeout > 0 else None

        users_list.append({
            "username": session['user'],
            "ip":session['address'],
            "connexion_time": session['uptime'],
            "expire_in": expire_in // 60 if expire_in else 0
        })

    return users_list


def users_no_expired(microtik_slug):
    microtik = Microtik.objects.filter(slug=microtik_slug).first()
    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    
    api = connection.get_api()

    user_resource = api.get_resource('/ip/hotspot/user')
    all_users = user_resource.get()

    user_list = []
    for user in all_users:
        limit = user.get('limit-uptime')
        used = user.get('uptime', '0s')
        
        if limit and used != limit:
            user_list.append({
                'name': user.get('name'),
                'limit_uptime': limit,
                'uptime': used,
                'address': user.get('address'),
                'profile': user.get('profile'),
                'disabled': user.get('disabled')
            })


def info_deposit_list(microtik_slug:str,owner:User):
    return InfoDeposit.objects.filter(microtik__slug=microtik_slug)

def info_deposit_retrive(microtik_slug:str,deposit_slug:str,owner:User):
    info_depot = InfoDeposit.objects.filter(
        slug = deposit_slug,
        microtik__slug=microtik_slug,
        ).first()

    if not info_depot:
        raise HttpError(
            status_code=404,
            message="Aucun client avec ce slug trouver."
        )
    return info_depot
