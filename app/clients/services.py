from datetime import datetime
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import InfoDeposit, Client
from typing import TYPE_CHECKING
from django.db import transaction
from app.utils.def_utils import connect_microtik, generer_code_unique

if TYPE_CHECKING:
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
        list_user.add(
            name=code_paye, 
            password=code_paye, 
            profile=profile_name,
            limit_uptime = limit_uptime,
            comment=f"Date: {datetime.fromtimestamp(timezone.now())} Payé via Djanto wifi"
        )
        return {"status":True,"message":f"success"}
    
    except Exception as e:
        if "already exists" in str(e).lower():
            pass

        return {"status":False,"message":f"Erreur MikroTik : {e}"}
    
    finally:
        connection.disconnect()
        


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
            get_code = generer_code_unique()

        create_user_api = creer_ticket_code(
            microtik=microtik,
            code_paye=get_code,
            profile=deposit.profil_name,
            limit_uptime=deposit.limit_uptime
        )

        if create_user_api.get('status') is True:
            client = Client.objects.create(
                phone_number = deposit.number_receve_code,
                code_username = get_code,
                code_password = get_code,
                microtik = microtik,
                limit_uptime = deposit.limit_uptime,
                profil_name= deposit.profil_name
            )

            deposit.status = InfoDeposit.SUCCESS
            deposit.eventId = eventId
            deposit.client = client
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
        