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

from app.clients.services import (
    deposit,
    notif_url,
    create_client_service ,
    list_client_service,
    actif_list_client_service,
    blocked_unlocked_client_service,
    no_expired_client_service,
    retrieve_client_service,

    
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
        response=list[ClientCreateResponse],
        description="La route pour le creation des clients par le owner microtik"
        )
def create_clients(request,data:ClientIn,microtik_slug:str):
    return create_client_service(
        microtik_slug=microtik_slug,
        profil_slug=data.profil_slug,
        user_numbers=data.user_numbers
    )


@client_router.patch(
        "/{microtik_slug}/bloked-client/{user_slug}",
        response=ClientBlockedOutSchemas,
        description="Le blocage d'un utilisateur."
        )
def block_client(request,microtik_slug:str,user_slug:str) -> ClientBlockedOutSchemas:

    return blocked_unlocked_client_service(
        microtik_slug=microtik_slug,
        user_slug=user_slug,
        is_desable=True
    )


@client_router.patch(
        "/{microtik_slug}/unblok-client/{user_slug}",
        description="la route pour le deblocage d'un client"
        )
def unblock_client(request,microtik_slug:str,user_slug:str) -> ClientBlockedOutSchemas:

    return blocked_unlocked_client_service(
        microtik_slug=microtik_slug,
        user_slug=user_slug,
        is_desable=False
    )


@client_router.get(
        "{microtik_slug}/list-client",
        response=list[ClientOut]
        )
def list_client(request,microtik_slug:str) -> list[ClientOut]:
    owner = request.user
    return list_client_service(microtik_slug=microtik_slug,owner=owner)


@client_router.get(
        "{microtik_slug}/retrieve-client/{client_slug}",
        response=list[ClientRetrieve]
        )
def retrieve_client(request,microtik_slug:str,client_slug:str) -> list[ClientRetrieve]:
    owner = request.user
    return retrieve_client_service(
        microtik_slug=microtik_slug,
        client_slug=client_slug,
        owner=owner
        )


@client_router.get(
        "{microtik_slug}/actif-client",
        response=list[ClientActifSchema]
        )
def actif_client(request,microtik_slug:str) -> list[ClientActifSchema]:
    return actif_list_client_service(
        microtik_slug=microtik_slug
    )


@client_router.get(
        "{microtik_slug}/no-expired-client", 
        response=list[ClientNoExpireSchema]
        )
def non_expire_client(request,microtik_slug:str) -> list[ClientNoExpireSchema]:
    return no_expired_client_service(
        microtik_slug=microtik_slug
    )

