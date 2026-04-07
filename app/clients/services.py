from datetime import datetime
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import InfoDeposit, Client
from typing import TYPE_CHECKING
from django.db import transaction
from app.utils.def_utils import connect_microtik, generer_code_unique, creer_ticket_code
from app.users.models import User
from django.db import transaction

if TYPE_CHECKING:
    from app.microtiks.models import Microtik



def deposit(microtik_slug:str,data:dict):
    microtik = Microtik.objects.prefetch_related("profils").filter(slug = microtik_slug).first()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="aucun microtik exitant avec ce slug."
        )
    profil_slug = data.get("profil_slug","") 
    profil = microtik.profils.filter(slug=profil_slug).first()
    if not profil:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspond a ce profil."
        )
    #appel api pour initier le depot
    #le transaction_id doit etre le slug du deposit.
    InfoDeposit.objects.create(
        **data, 
        microtik=microtik,
        profil_name=profil.name,
        limit_uptime=profil.rate_limit,
        amount=profil.price
        )
    return {"status":"success", "message":"Retrait initier avec success."}


@transaction.atomic()
def notif_url(data:str) -> dict:
    eventId = data.get("eventId","")
        
    data_transaction = data.get("data", {})
    transactionId = data_transaction.get("transactionId","")
    status = data_transaction.get("status", "")

    deposit = InfoDeposit.objects.select_related("info_deposit").filter(slug=transactionId).first()
    microtik = deposit.microtik

    if status == "SUCCESS":
        
        get_code = generer_code_unique(longueur=10)

        while Client.objects.filter(code_username=get_code,microtik=microtik).exists():
            get_code = list(generer_code_unique())

        create_user_api = creer_ticket_code(
            microtik=microtik,
            code_paye=get_code,
            profile=deposit.profil_name,
            limit_uptime=deposit.limit_uptime,
            comment=f"Date: {datetime.fromtimestamp(timezone.now())} Payé via Djanto wifi"
        )

        if create_user_api.get('status') is True:
            Client.objects.create(
                phone_number = deposit.number_receve_code,
                code_username = get_code,
                code_password = get_code,
                microtik = microtik,
                info_deposit = deposit,
                limit_uptime = deposit.limit_uptime,
                profil_name= deposit.profil_name
            )

            deposit.status = InfoDeposit.SUCCESS
            deposit.eventId = eventId
            deposit.save()

            microtik.sold += deposit.amount
            microtik.users += 1
            microtik.save()

            #envoie du sms

    else:
        deposit.status = InfoDeposit.FAILED
        deposit.eventId = eventId
        deposit.save()
    
    return {}
        
        

def create_client_service(microtik_slug,profil_slug,user_numbers):
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
        limit_uptime=profil.session_timeout,
        comment=f"Date: {datetime.fromtimestamp(timezone.now())} admin generation"
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


def list_client_service(microtik_slug:str,owner:User) -> list[User]:
    microtik = Microtik.objects.prefetch_related("clients").filter(slug=microtik_slug,owner=owner).first()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspondant a ce microtik."
        )
    users = microtik.clients.all()
    return users


def retrieve_client_service(microtik_slug:str,client_slug:str,owner:User) -> User:
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


def blocked_unlocked_client_service(microtik_slug:str,user_slug:str,is_desable:bool):
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


def actif_list_client_service(microtik_slug):
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


def no_expired_client_service(microtik_slug):
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
