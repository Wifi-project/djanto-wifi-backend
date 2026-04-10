from ninja.errors import HttpError
from http import HTTPStatus
from typing import TYPE_CHECKING

from app.subscriptions.models import SubscriptionVpn
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

    

