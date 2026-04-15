from __future__ import annotations
from ninja.errors import HttpError
from http import HTTPStatus
from typing import TYPE_CHECKING
import ipaddress
from app.utils.vpn_user import create_vpn_user
from app.utils.def_utils import generer_code_unique
from app.api_extern.adapterPayement import AdapterPayement


from app.subscriptions.models import SubscriptionVpn,SubscriptionCategorieVpn
if TYPE_CHECKING:
    from app.microtiks.models import Microtik


def update_subscrib_vpn(slug,data:dict):
    instance = SubscriptionVpn.objects.filter(slug=slug).first()
    if not instance:
        raise HttpError(
            status_code=404,
            message="Aucune suscription existant avec ce slug"
        )
    
    for key,value in data.items():
        setattr(instance, key,value)
    instance.save()

    return instance


async def subscrition_abonnement_service(data:dict, microtik:Microtik):
    phone_number = data.get('phone_number',"")
    category_slug = data.get("category_slug","")
    paymentMethod = data.get('paymentMethod', "")

    if not category_slug and phone_number:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Vous n'avez pas selectionner le type d'abonnement et le numero pour le paiement."
        )
    
    category = await SubscriptionCategorieVpn.objects.filter(slug=category_slug).afirst()

    adapter = AdapterPayement(code="djomy")
    response = await adapter.payement(
        amount=category.price,
        method=paymentMethod,
        reference=microtik.slug,
        number=phone_number
    )
    return response



# def return_url(data:dict):
    # IP_DE_DEPART = "172.16.0.10"

#     count_user = SubscriptionCategorieVpn.objects.count()
#     code = generer_code_unique()
#     name = microtik.name.split('')[0]
#     username = name + code 

#     ip = str(ipaddress.IPv4Address(IP_DE_DEPART) + count_user)

#     response = create_vpn_user(username=username,password= code,ip=ip)
#     if not response:
#         raise 
#     subscription = SubscriptionVpn.objects.create(
#         vpn_username = username,
#         vpn_password = code,
#         vpn_ip = ip,
#         category = category
#         )
    
#     microtik.subscription = subscription
#     microtik.save()

#     return True
