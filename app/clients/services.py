from __future__ import annotations
from datetime import datetime
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import  Client,Status
from typing import TYPE_CHECKING
from app.users.models import User
from django.db import transaction
from app.api_extern.adapterPayement import AdapterPayement
# from app.clients.tasks import process_payment_webhook_task
from app.gdms.api_gdms import gdms_service
from app.clients.models import GroupClient
from app.gdms.models import Network
from app.gdms.models import Profil



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
    #----------------------La gestion voucher-----------------------
    @staticmethod
    async def create_voucher_service(network:Network,profil_slug,voucher_number):
        profil = network.profils.filter(slug=profil_slug).first()
        name = f"voucher_{profil.name}-{timezone.now()}"
        if not profil:
            raise HttpError(
                status_code=HTTPStatus.BAD_REQUEST,
                message="Aucun slug correspondant a ce profil."
            )

        tickets = None 

        tickets = await gdms_service.create_vouchers(
            network_id= network.network_id,
            upRate= profil.up_rate,
            downRate=profil.down_rate,
            name = name,
            count=voucher_number,
            effect_duration_map=profil.session_timeout_dict,
            max_devices= profil.shared_users,
        )
        if tickets.get('status'):
            GroupClient.objects.create(
                name = name,
                network = network,
                number_voucher = voucher_number
            )
            return {'status':'success','message':"la generation effecuteur avec success."}

        raise HttpError(
            status_code=504,
            message=f"une erreur lors de la generation des coupons "
        )

            
    @staticmethod
    async def list_voucher_group_service(network: Network,page_size:int=10, page_num:int=1,search:str | None = None) -> dict:
        res = await gdms_service.list_group_voucher(
            network_id=network.network_id,
            page_size=page_size,
            page_num=page_num,
            search = search
        )
        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"une erreur backend s'est produit {res.get('message')}"
            )

        return res.get('message')


    @staticmethod
    async def list_voucher_in_group_service(network: Network,group_id:int,search:str | None = None) -> dict:
        res = await gdms_service.list_voucher_in_group(
            network_id=network.network_id,
            group_id=group_id,
            search = search
        )
        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"une erreur backend s'est produit {res.get('message')}"
            )

        return res.get('message')



    @staticmethod
    async def delete_voucher_service(network: Network,voucher_id:int):
        res = gdms_service.delete_voucher(
            voucher_id=voucher_id,
            network_id=network.network_id
        )

        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Une erreur lors de la suppression {res.get('message')}"
            )

        return {'status':'success', 'message':"la suppression effectuer avec success."}


    #---------------la gestion client--------------------------------
    @staticmethod
    async def list_client_service(start_at:int,end_at:int,network: Network, page_num:int=1, page_size:int=10) -> dict:
        """Afficher le liste des clients"""
        response = await gdms_service.list_clients(
            network_id=network.network_id,
            page_num=page_num,
            page_size=page_size,
            start_at=start_at,
            end_date=end_at
        )

        if not response.get('status'):
            raise HttpError(
                status_code=500,
                message=f"Une erreur f{response.get('message')}"
            )

        return response.get("message")


    # @staticmethod
    # def retrieve_client_service(microtik: Microtik,subscription:SubscriptionWG, client_id: str) -> Client:
    #     """ Afficher les details user d'un microtik """
    #     res = gdms_service.client_retrieve(
    #         network_id=subscription.gdms_network_id,
    #         client_id=client_id
    #     )

    #     client = Client.objects.filter(client_id=client_id).first()
    #     client.status = Status.DISABLE
    #     client.save(update_fields=['status'])
    #     return res


    @staticmethod
    async def blocked_unlocked_client_service(network: Network, client_id: str, enable: bool):

        response = await gdms_service.block_disblock_client(
            network_id=network.network_id,
            client_id=client_id,
            enable=enable
        )
        if not response.get('status'):
            raise HttpError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message='une erreur inatandu sest produit'
            )
        
        return {'status':'success','message':'Le client blocker avec success.'}
        


    @staticmethod
    async def actif_list_client_service(network: Network, page_num:int=10, page_size:int=0) -> dict[str,str]:
        
        res = await gdms_service.get_online_guests(
            network_id=network.network_id,
            page_num=page_num,
            page_size=page_size
        ) 

        if not res.get("status"):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Une erreur {res.get('message')}"
            )
        
        return res.get("message")


    # @staticmethod
    # def kick_client_service(microtik: Microtik, username: str, subscription: SubscriptionWG) -> dict:
    #     """Expulse un utilisateur de la session active sans désactiver son ticket."""
    #     res = gdms_service.kick_guest(

    #     )


    @staticmethod
    def reset_uptime_service(microtik: Microtik, user_slug: str, subscription: SubscriptionWG) -> dict:
        """Réinitialise les compteurs de consommation (temps et octets) d'un utilisateur sur le MikroTik."""
        ...



