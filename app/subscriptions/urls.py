from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate

from app.subscriptions.models import SubscriptionCategorieVpn,SubscriptionVpn
from app.subscriptions.schemas import (
    SubscriptionCategorieIntSchema,
    SubscriptionCategorieOutShema,
    SubscriptionCategorieUpdateSchema,
    SubscriptionVpnInSchema,
    SubscriptionResponse
    )
from app.users.deps import GlobalAuth
from app.subscriptions.services import update_subscrib_vpn


subscription = Router(tags=["Subscription-Vpn"], auth=GlobalAuth([]))


@subscription.post("/categories", response=SubscriptionCategorieOutShema) 
def create(request,data:SubscriptionCategorieIntSchema)-> SubscriptionCategorieOutShema:
    return SubscriptionCategorieVpn.objects.create(**data.model_dump())


@subscription.get("/categories", response=list[SubscriptionCategorieOutShema])
def get(request) -> list[SubscriptionCategorieOutShema]:
    user = request.user 
    if user and user.user_type and user.user_type == "admin":
        return SubscriptionCategorieVpn.objects.all()
    return SubscriptionCategorieVpn.objects.filter(is_active=True)


@subscription.patch("/categories/{slug}")
def update(request,slug,data:SubscriptionCategorieUpdateSchema) -> SubscriptionCategorieOutShema:
    return update_subscrib_vpn(slug, data=data.model_dump())


#------------------------- Subscription -------------------------------#

@subscription.post("/", response=SubscriptionResponse)
def suscrib_abonement(request,data:SubscriptionVpnInSchema) -> SubscriptionResponse:
    #call api de paiement
    return {"status":"success", "message":"retrait pour l'abonnement initier avec success"}

