from __future__ import annotations
from datetime import datetime
from django.utils import timezone
from ninja.errors import HttpError
from http import HTTPStatus
from app.clients.models import  Client,Status
from typing import TYPE_CHECKING
from app.users.models import User
from django.db import transaction
from app.api_extern.adapterPayement import adapeter_payement
from django.db import transaction as db_transaction
from app.gdms.api_gdms import gdms_service
from app.clients.models import GroupClient
from app.gdms.models import Network
from app.gdms.models import Profil
from asgiref.sync import async_to_sync
from app.transactions.models import Transaction,TransactionType,PaymentMethod,TransactionStatus
import secrets
from app.api_extern.nimba_sms import send_sms
from app.commone.email import sender_email

async def deposit_voucher(network_slug: str, data: dict):
    payementMethod = data.get('paymentMethod', "")
    profil_slug = data.get("profil_slug", "")
    phone_number = data.get('phone_number', "")

    network = await Network.objects.filter(slug=network_slug,status= Status.ACTIVE,admin_blocked=False).afirst()
    if not network:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Erreur ce reseau nest pas disponible."
        )
    
    if not payementMethod or not profil_slug or not phone_number:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Erreur le veuillez vous rassurer que tous les champs sont renseigner."
        )

    payemant_method = await PaymentMethod.objects.filter(code=payementMethod, is_active=True).afirst()
    profile = await Profil.objects.filter(slug = profil_slug).afirst()

    if not payemant_method or not profile:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"Erreur le moyen de payement selectionne ou profil n'est pas disponible. "
        )

    transaction_init = await Transaction.objects.acreate(
        phone_number = phone_number,
        amount = profile.price,
        network = network,
        network_description = network.description,
        network_name = network.name,
        profil= profile,
        payment_method = payemant_method.code,
        type = TransactionType.VOUCHER_PURCHASE
    )

    response = await adapeter_payement.payeIn(
        amount=profile.price,
        method=payemant_method.code,
        number=phone_number,
        reference="",
        description=f"achat de voucher par om sur le {network.name}"
    )

    if response and response.get("transactionId"):
        transaction_init.transaction_id = response.get("transactionId")
        await transaction_init.asave(update_fields=['transaction_id'])
    
        return {
            'status':'success',
            'message':'payement initier avec success.'
        }

    return {
        'status':'failled',
        'message':"Erreur d'initialisation de paiement."
    }



import secrets
from asgiref.sync import async_to_sync
from django.db import transaction as db_transaction

def webhook_voucher(transaction: Transaction) -> dict:
    """
    Webhook de notification de paiement.
    Gère la validation du paiement, la création du ticket sur le MikroTik
    et la mise à jour de la base de données.
    """
    network = transaction.network
    phone_number = transaction.phone_number
    profil = transaction.profil

    network.wallet_balance = network.wallet_balance + transaction.amount
    network.save(update_fields=['wallet_balance'])

    need_generation = False
    with db_transaction.atomic():
        if not Client.objects.filter(network=network, buy=False).exists():
            need_generation = True

    if need_generation:
        name = f"systeme_voucher_{secrets.token_urlsafe(10)}"
        
        group_voucher = async_to_sync(gdms_service.create_vouchers)(
            network_id=network.network_id,
            upRate=profil.up_rate,
            downRate=profil.down_rate,
            name=name,
            count=500,
            effect_duration_map=profil.session_timeout_dict,
            max_devices=profil.shared_users,
        )
        
        if not group_voucher or not group_voucher.get('status'):
            raise Exception("Échec de la création des vouchers sur GDMS")

        response_new_voucher_list = async_to_sync(gdms_service.list_group_voucher)(
            network_id=network.network_id,
            page_num=1,
            page_size=10,
            search=name
        )

        if not response_new_voucher_list or not response_new_voucher_list.get('status'):
            raise Exception("Échec de la récupération du groupe de vouchers")

        data = response_new_voucher_list.get('data', {})
        result = data.get("result", [])

        if not result:
            raise Exception("Aucun groupe trouvé pour ce nom sur GDMS")

        current_group = result[0]
        current_group_id = current_group.get("id")
        
        if not current_group_id:
            raise Exception("ID du groupe GDMS introuvable")

        vouchers_list_data = async_to_sync(gdms_service.list_voucher_in_group)(
            group_id=current_group_id,
            network_id=network.network_id,
            page_num=1,
            page_size=500
        )

        voucher_result = vouchers_list_data.get('result', [])
        if not voucher_result:
            raise Exception("Aucun voucher retourné par le groupe GDMS")

        with db_transaction.atomic():
            if not Client.objects.filter(network=network, buy=False).exists():
                clients_to_create = [
                    Client(
                        code_password=voucher.get("password"),
                        code_username=voucher.get("password"),
                        network=network
                    )
                    for voucher in voucher_result if voucher.get("password")
                ]
                Client.objects.bulk_create(clients_to_create)


    with db_transaction.atomic():
        voucher = Client.objects.select_for_update(skip_locked=True).filter(network=network, buy=False).first()

        if not voucher:
            return {"status": "error", "message": "Aucun voucher disponible pour ce réseau."}

        voucher.buy = True
        voucher.save(update_fields=["buy"])

    response_sms = send_sms.send(
        phone_number,
        message=f"Votre voucher de connexion : \n {voucher.code_password} \n prix: {transaction.amount}"
    )

    if response_sms and response_sms.get('status') == "success":
        voucher.sms_send = True
        voucher.save(update_fields=["sms_send"])
        return {"status": "success", "message": "Voucher attribué et SMS envoyé."}
    
    return {"status": "warning", "message": "Voucher trouvé mais échec de l'envoi du SMS."}



class ClientService:
    #----------------------La gestion voucher-----------------------
    @staticmethod
    async def create_voucher_service(network:Network,profil_slug,voucher_number):
        profil = await network.profils.filter(slug=profil_slug).afirst()
        name = f"voucher_{profil.name}-{timezone.now().date()}-{secrets.token_urlsafe(2)}"
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
            GroupClient.objects.acreate(
                name = name,
                network = network,
                number_voucher = voucher_number
            )
            return {'status':'success','message':"la generation effecuteur avec success."}

        raise HttpError(
            status_code=504,
            message=f"une erreur lors de la generation des coupons {tickets.get('data')} "
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
                message=f"une erreur backend s'est produit {res.get('data')}"
            )
        return res.get('data')


    @staticmethod
    async def list_voucher_in_group_service(network: Network,page_num:int,page_size:int,group_id:int,search:str | None = None) -> dict:
        res = await gdms_service.list_voucher_in_group(
            network_id=network.network_id,
            group_id=group_id,
            search = search,
            page_num=page_num,
            page_size=page_size
        )
        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"une erreur backend s'est produit {res.get('data')}"
            )
        
        return res.get('data')



    @staticmethod
    async def delete_voucher_service(network: Network,voucher_id:int):
        res = await gdms_service.delete_voucher(
            voucher_id=voucher_id,
            network_id=network.network_id
        )

        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Une erreur lors de la suppression {res.get('data')}"
            )

        return {'status':'success', 'message':"la suppression effectuer avec success."}



    @staticmethod
    async def delete_voucher_group_service(network: Network,group_id:list):
        res = await gdms_service.delete_voucher_group(
            group_id=group_id,
            network_id=network.network_id
        )

        if not res.get('status'):
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Une erreur lors de la suppression {res.get('data')}"
            )

        return {'status':'success', 'message':"la suppression effectuer avec success."}


    #---------------la gestion client--------------------------------
    @staticmethod
    async def list_client_service(network: Network,start_at:int|None = None,end_at:int|None = None, page_num:int=1, page_size:int=10) -> dict:
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
                message=f"Une erreur f{response.get('data')}"
            )
        return response.get("data")


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
                message=f'une erreur inatandu sest produit {response.get("data")}'
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
                message=f"Une erreur {res.get('data')}"
            )
        
        return res.get("data")


    # @staticmethod
    # def kick_client_service(microtik: Microtik, username: str, subscription: SubscriptionWG) -> dict:
    #     """Expulse un utilisateur de la session active sans désactiver son ticket."""
    #     res = gdms_service.kick_guest(

    #     )




