from __future__ import annotations
from ninja.errors import HttpError
from http import HTTPStatus
from typing import TYPE_CHECKING
from app.api_extern.adapterPayement import AdapterPayement
from app.subscriptions.models import (
    SubscriptionCategorie, 
    SubscriptioPriceBase,

    )
from asgiref.sync import sync_to_async
from decimal import Decimal
# from app.subscriptions.tasks import subscription_webhook_task
from app.transactions.models import Transaction,TransactionStatus,TransactionType
from app.subscriptions.models import ConfigurationPrice
from app.gdms.models import Network
from django.utils import timezone
from datetime import timedelta
from app.subscriptions.models import SubscriptionCategorie




#--------------- Prix de base ----------------------~#

def create_price_base_service(data:dict):
    if SubscriptioPriceBase.objects.all().exists():
        raise HttpError(
            status_code = 404,
            message = "Un prix de base existe deja veillez modifier celui ci."
        )
    return SubscriptioPriceBase.objects.create(**data)


def update_price_base_service(slug: str, data: dict) -> SubscriptioPriceBase:
    try:
        instance = SubscriptioPriceBase.objects.get(slug=slug)
    except SubscriptioPriceBase.DoesNotExist:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun prix ne correspond à ce slug"
        )

    for attr, value in data.items():
        setattr(instance, attr, value)
    
    instance.save()
    return instance


#--------------- Categories abonnement ---------------#

def _naturalize_days(days: int = 0, months: int = 0) -> int:
    """Convertit les mois en jours (1 mois = 30 jours)"""
    return days + (months * 30)


def create_categorie_abonnement(data: dict) -> SubscriptionCategorie:
    days = data.get("days", 0)
    months = data.get("months", 0)
    name = data.get("name", "").strip()
    discount = data.get("discount", 0.0)

    total_days = _naturalize_days(days=days, months=months)

    if total_days <= 0:
        raise HttpError(
            status_code=400,
            message="La durée totale doit être supérieure à 0"
        )

    if discount < 0 or discount > 100:
        raise HttpError(
            status_code=400,
            message="La remise doit être comprise entre 0 et 100%"
        )

    price_base = SubscriptioPriceBase.objects.filter(is_active=True).first()
    if not price_base:
        raise HttpError(
            status_code=404,
            message="Aucun prix de base actif trouvé"
        )

    discount_decimal = Decimal(str(discount))
    price_base_decimal = price_base.price

    price = price_base_decimal * (Decimal('1') - discount_decimal / Decimal('100'))
    
    price = price.quantize(Decimal('0.01')) * total_days

    return SubscriptionCategorie.objects.create(
        name=name,
        days=total_days,
        price=price,
        discount=discount
    )




def update_categorie_abonnement(slug,data:dict) -> SubscriptionCategorie:
    days = data.pop("days",0)
    months = data.pop("months",0)
    total_days = _naturalize_days(days=days,months=months)

    data["days"] = total_days if total_days > 0 else ...

    instance = SubscriptionCategorie.objects.filter(slug=slug).first()
    
    if not instance:
        raise HttpError(
            status_code=404,
            message="Aucune suscription existant avec ce slug"
        )
    
    for key,value in data.items():
        setattr(instance, key,value)
    instance.save()

    return instance


#------------- La suscription aux abonement --------------- #

async def subscrition_abonnement_service(data: dict, network: Network): 
    phone_number = data.get('phone_number', "") 
    category_slug = data.get("category_slug", "") 
    paymentMethod = data.get('paymentMethod', "") 
    
    if not category_slug or not phone_number: 
        raise HttpError( 
            status_code=HTTPStatus.BAD_REQUEST, 
            message="Vous devez sélectionner le type d'abonnement et le numéro pour le paiement." 
        ) 
        
    try: 
        category = await SubscriptionCategorie.objects.aget(slug=category_slug) 
    except SubscriptionCategorie.DoesNotExist: 
        raise HttpError( 
            status_code=HTTPStatus.NOT_FOUND, 
            message="Catégorie d'abonnement non trouvée" 
        ) 

    if not network.configuration_paid:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Vous devez d'abord payer les frais de configurations."
        )
    
    transaction = await Transaction.objects.acreate( 
        phone_number=phone_number,
        amount = category.price,
        network = network,
        category=category, 
        payment_method = paymentMethod,
        status=TransactionStatus.PENDING,
        type = TransactionType.SUBSCRIPTION
    ) 
        
    adapter = AdapterPayement(code="djomy") 
    response = await adapter.payeIn( 
        amount=category.price, 
        method=paymentMethod, 
        reference=transaction.slug, 
        number=phone_number, 
        description="Abonnement access a distance." 
    ) 

    if response and response.get("transactionId"):
        transaction.transaction_id = response.get("transactionId")
        await transaction.asave(update_fields=['transaction_id'])

        network.subscription_at = timezone.now()
        network.subscription_expire_at = timezone.now() + timedelta(days=transaction.category.days)
        await network.asave(update_fields=["subscription_expire_at"])
    
        return {
            'status':'success',
            'message':'payement initier avec success.'
        }


    return {
        'status':'failled',
        'message':'initiation du payement echouer.'
    }



async def init_configuration(network:Network, data:dict):
    price = await  ConfigurationPrice.objects.afirst()
    paymentMethod = data.get('paymentMethod')
    phone = data.get('phone_number')
    
    transaction = await Transaction.objects.acreate( 
        phone_number= phone,
        amount = price.price,
        network = network,
        payment_method = paymentMethod,
        status=TransactionStatus.PENDING,
        type = TransactionType.CONFIGURATION
    ) 
        
    adapter = AdapterPayement(code="djomy") 
    response = await adapter.payeIn( 
        amount=price.price, 
        method=paymentMethod, 
        reference=transaction.slug, 
        number=phone, 
        description="Suscription a la configuration access a distance." 
    ) 

    if response and response.get("transactionId"):
        transaction.transaction_id = response.get("transactionId")
        await transaction.asave(update_fields=['transaction_id'])

        network.subscription_at = timezone.now()
        network.configuration_paid = True
        network.subscription_expire_at = timezone.now() + timedelta(days=30)
        await network.asave(update_fields=["subscription_expire_at","configuration_paid"])

        return {
            'status':'success',
            'message':'initiation du payement de configuration effectuer avec success.'
        }

    return {
        'status':'failled',
        'message':'initiation du payement echouer.'
    }


# def return_url(data: dict):
#     """Callback après paiement"""
#     subscription_webhook_task.delay(data=data)