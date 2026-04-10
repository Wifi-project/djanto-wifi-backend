from ninja import Router

from app.clients.schemas import (
    InfoDepositIn,
    DepositResponseSchemas,
    PaymentWebhook,
    ClientIn,
    ClientCreateResponse,
    ClientOut,
    ClientActifSchema,
    ClientNoExpireSchema,
    ClientBlockedOutSchemas,
    ClientRetrieve,
)
from app.users.deps import GlobalAuth,MicrotikAuth,SubscriptionVpn

from app.clients.services import (
    deposit,
    notif_url,
    ClientService
    )


client_router = Router(tags=["Client"])


@client_router.post("/deposit/{microtik_slug}", response=DepositResponseSchemas)
def deposit_client(request,data:InfoDepositIn, microtik_slug:str) -> DepositResponseSchemas:
    return deposit(microtik_slug=microtik_slug,data=data.model_dump())


@client_router.post("/notif/reponse/transaction/")
def notifiurl(request,data:PaymentWebhook):
    return notif_url(
        data=data.model_dump()
    )


@client_router.post(
        "/{microtik_slug}/create-client", 
        auth=[GlobalAuth(),MicrotikAuth(),SubscriptionVpn()],
        response=list[ClientCreateResponse],
        description="La route pour le creation des clients par le owner microtik"
        )
def create_clients(request,data:ClientIn):
    return ClientService.create_client_service(
        microtik=request.microtik,
        profil_slug=data.profil_slug,
        user_numbers=data.user_numbers
    )


@client_router.patch(
        "/{microtik_slug}/bloked-client/{user_slug}",
        auth=[GlobalAuth(),MicrotikAuth(),SubscriptionVpn()],
        response=ClientBlockedOutSchemas,
        description="Le blocage d'un utilisateur."
        )
def block_client(request,user_slug:str) -> ClientBlockedOutSchemas:

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        vpn = request.vpn,
        user_slug=user_slug,
        is_desable=True
    )


@client_router.patch(
        "/{microtik_slug}/unblok-client/{user_slug}",
        auth=[GlobalAuth(),MicrotikAuth(),SubscriptionVpn()],
        description="la route pour le deblocage d'un client"
        )
def unblock_client(request,user_slug:str) -> ClientBlockedOutSchemas:

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        vpn= request.vpn,
        user_slug=user_slug,
        is_desable=False
    )


@client_router.get(
        "{microtik_slug}/list-client",
        auth=[GlobalAuth(),MicrotikAuth()],
        response=list[ClientOut]
        )
def list_client(request) -> list[ClientOut]:
    return ClientService.list_client_service(
        microtik=request.microtik,
        )


@client_router.get(
        "{microtik_slug}/retrieve-client/{client_slug}",
        auth=[GlobalAuth(),MicrotikAuth()],
        response=list[ClientRetrieve]
        )
def retrieve_client(request,client_slug:str) -> list[ClientRetrieve]:
    return ClientService.retrieve_client_service(
        microtik=request.microtik,
        client_slug=client_slug,
        )


@client_router.get(
        "{microtik_slug}/actif-client",
        auth=[GlobalAuth(),MicrotikAuth(),SubscriptionVpn()],
        response=list[ClientActifSchema]
        )
def actif_client(request) -> list[ClientActifSchema]:
    return ClientService.actif_list_client_service(
        microtik=request.microtik,
        vpn=request.vpn
    )


@client_router.get(
        "{microtik_slug}/no-expired-client", 
        auth=[GlobalAuth(),MicrotikAuth(),SubscriptionVpn()],
        response=list[ClientNoExpireSchema]
        )
def non_expire_client(request) -> list[ClientNoExpireSchema]:
    return ClientService.no_expired_client_service(
        microtik=request.microtik
    )

