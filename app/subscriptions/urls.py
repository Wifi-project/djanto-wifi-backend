from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from app.api_extern.adapterPayement import AdapterPayement
from app.subscriptions.models import SubscriptionCategorieVpn,SubscriptionVpn
from app.subscriptions.schemas import (
    SubscriptionCategorieIntSchema,
    SubscriptionCategorieOutShema,
    SubscriptionCategorieUpdateSchema,
    SubscriptionVpnInSchema,
    SubscriptionResponse
    )
from app.users.deps import GlobalAuth,Auth,IsOwnerMicrotik,HasValidVpn
from app.subscriptions.services import update_subscrib_vpn,subscrition_abonnement_service


subscription = Router(tags=["Subscription-Vpn"], auth=GlobalAuth())


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

@subscription.post(
        "/{microtik_slug}",
        # response=SubscriptionResponse,
        auth=GlobalAuth(permissions=[Auth,IsOwnerMicrotik])
        )
async def suscrib_abonement(request,data:SubscriptionVpnInSchema,microtik_slug:str) -> SubscriptionResponse:
    return await subscrition_abonnement_service(
        data=data.model_dump(),
        microtik=request.microtik
        )

