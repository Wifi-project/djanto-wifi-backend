from __future__ import annotations
from datetime import datetime
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import InfoDeposit, Client,Status
from typing import TYPE_CHECKING
from django.db import transaction
from app.users.models import User
from django.db import transaction
from app.subscriptions.models import SubscriptionWG
from app.api_extern.adapterPayement import AdapterPayement
import csv
from app.clients.tasks import process_payment_webhook_task
from app.microtiks.gms import gdms_service
from app.clients.models import GroupClient


if TYPE_CHECKING:
    from app.microtiks.models import Microtik,RouteurType,Profil




async def deposit(microtik_slug: str, data: dict):
    from app.microtiks.models import Microtik
    
    microtik = await Microtik.objects.prefetch_related("profils").filter(slug=microtik_slug).afirst()
    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="aucun microtik existant avec ce slug."
        )
    
    profil_slug = data.pop("profil_slug", "") 
    profil = await microtik.profils.filter(slug=profil_slug).afirst()
    if not profil:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun slug correspond a ce profil."
        )
    
    adapter = AdapterPayement(code="djomy")
    
    reference = await InfoDeposit.objects.acreate(
        **data, 
        microtik=microtik,
        profil_name=profil.name,
        limit_uptime=profil.rate_limit,
        amount=profil.price
    )
    
    response = await adapter.payeIn(
        amount=profil.price,
        method=data.get("paymentMethod"),
        number=data.get("phone_number"),
        reference=reference.slug,
        description = " Achat de ticket"
    )
    
    return response



def notif_url(data: dict) -> dict:
    """
    Webhook de notification de paiement.
    Gère la validation du paiement, la création du ticket sur le MikroTik
    et la mise à jour de la base de données.
    """
    return process_payment_webhook_task.delay(data=data)         


class ClientService:

    @staticmethod
    def list_group(microtik:Microtik):
        group = GroupClient.objects.filter(microtik=microtik).order_by('-created_at')
        return group


    @staticmethod
    async def create_voucher_service(microtik:Microtik,profil_slug,voucher_number):
        profil = microtik.profils.filter(slug=profil_slug).first()

        if not profil:
            raise HttpError(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Aucun slug correspondant a ce profil."
            )

        device_type = microtik.device_type
        subs = microtik.subscriptionwg
        tickets = None 

        if device_type == RouteurType.GDMS.value:
            tickets = await gdms_service.create_vouchers(
                network_id= subs.gdms_network_id,
                upRate= profil.up_rate,
                downRate=profil.down_rate,
                name = f"voucher_{profil.name}-{timezone.now()}",
                count=voucher_number,
                effect_duration_map=profil.session_timeout_dict,
                max_devices= profil.shared_users,
            )
            if tickets:
                GroupClient.objects.create(
                    name = f"voucher_{profil.name}-{timezone.now()}",
                    microtik = microtik,
                    number_voucher = voucher_number
                )
                print('les tickets: \n', tickets)

            
    @staticmethod
    async def list_voucher_service(microtik: Microtik, subscription: SubscriptionWG,page_size:int=10, page_num:int=1) -> dict:
        res = await gdms_service.list_voucher(
            network_id=subscription.gdms_network_id,
            page_size=page_size,
            page_num=page_num
        )
        return res


    @staticmethod
    async def delete_voucher_service(microtik: Microtik, subscription: SubscriptionWG,voucher_id:int):
        res = gdms_service.delete_voucher(
            voucher_id=voucher_id,
            network_id=subscription.gdms_network_id
        )
        if not res:
            ...

        return res


    @staticmethod
    def list_client_service(microtik: Microtik, subscription: SubscriptionWG, page_num:int=1, page_size:int=10) -> dict:
        """Afficher le liste des clients"""
        response = gdms_service.list_clients(
            network_id=subscription.gdms_network_id,
            page_num=page_num,
            page_size=page_size
        )
        return response


    @staticmethod
    def retrieve_client_service(microtik: Microtik,subscription:SubscriptionWG, client_id: str) -> Client:
        """ Afficher les details user d'un microtik """
        res = gdms_service.client_retrieve(
            network_id=subscription.gdms_network_id,
            client_id=client_id
        )

        client = Client.objects.filter(client_id=client_id).first()
        client.status = Status.DISABLE
        client.save(update_fields=['status'])
        return res


    @staticmethod
    async def blocked_unlocked_client_service(microtik: Microtik, client_id: str, enable: bool, subscription: SubscriptionWG):
        client = microtik.clients.filter(client_id=client_id).first()
        if not client:
            raise HttpError(
                status_code=HTTPStatus.BAD_REQUEST,
                message="le slug de ce client n'existe pas."
            )

        response = gdms_service.block_disblock_client(
            network_id=subscription.gdms_network_id,
            client_id=client_id,
            enable=enable
        )
        if not response:
            raise HttpError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message='une erreur inatandu sest produit'
            )
        
        client.status = Status.DISABLE if enable else Status.ACTIVE
        client.save()
        return client
        


    @staticmethod
    async def actif_list_client_service(microtik: Microtik, subscription: SubscriptionWG, page_num:int=10, page_size:int=0) -> list:
        
        res = gdms_service.get_online_guests(
            network_id=subscription.gdms_network_id,
            page_num=page_num,
            page_size=page_size
        ) 
        return res


    @staticmethod
    def kick_client_service(microtik: Microtik, username: str, subscription: SubscriptionWG) -> dict:
        """Expulse un utilisateur de la session active sans désactiver son ticket."""
        res = gdms_service.kick_guest(

        )


    @staticmethod
    def reset_uptime_service(microtik: Microtik, user_slug: str, subscription: SubscriptionWG) -> dict:
        """Réinitialise les compteurs de consommation (temps et octets) d'un utilisateur sur le MikroTik."""
        ...


    @staticmethod
    def csv_save_service(reader: csv.DictReader, microtik: Microtik):
        model_list = []

        for row in reader:
            # 1. On transforme toutes les clés de la ligne en minuscules et on nettoie les espaces/tirets
            row_lower = {k.lower().strip().replace("-", " "): v for k, v in row.items() if k}
            
            # 2. Extraction sécurisée selon les formats classiques de Mikhmon
            username = row_lower.get("username") or row_lower.get("login", "")
            password = row_lower.get("password") or row_lower.get("pwd", "")
            profile = row_lower.get("profile") or row_lower.get("upiprofile", "")
            
            # Gère les variantes de colonnes de Mikhmon ("limit uptime", "limit-uptime", "date limit")
            limit_uptime = row_lower.get("limit uptime") or row_lower.get("date limit") or row_lower.get("uptime", "")

            # Sécurité : On ignore les lignes complètement vides
            if not username:
                continue

            model_list.append(
                Client(
                    code_username=username, 
                    code_password=password, 
                    profil_name=profile,
                    limit_uptime=limit_uptime,
                    generate=Client.IMPORT,
                    microtik=microtik
                )
            )
        
        # 3. Sauvegarde de masse optimisée en BDD
        if model_list:
            clients = Client.objects.bulk_create(model_list, return_defaults=True)
            return clients
        
        return []



