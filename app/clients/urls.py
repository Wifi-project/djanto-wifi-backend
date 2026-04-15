from ninja import Router, File
import csv
import io
from ninja.files import UploadedFile

from app.clients.schemas import (
    InfoDepositIn,
    DepositResponseSchemas,
    PaymentResponseSchema,
    PaymentWebhook,
    ClientIn,
    ClientCreateResponse,
    ClientOut,
    ClientActifSchema,
    ClientNoExpireSchema,
    ClientBlockedOutSchemas,
    ClientRetrieve,
)
from app.users.deps import GlobalAuth,IsOwnerMicrotik,HasValidVpn,Auth

from app.clients.services import (
    deposit,
    notif_url,
    ClientService,
    )

client_router = Router(tags=["Client"])


@client_router.post("/deposit/{microtik_slug}", response=DepositResponseSchemas)
async def deposit_client(request,data:InfoDepositIn, microtik_slug:str) -> DepositResponseSchemas:
    return await deposit(microtik_slug=microtik_slug,data=data.model_dump())


@client_router.post("/notif/reponse/transaction/")
def notifiurl(request,data:PaymentWebhook):
    return notif_url(
        data=data.model_dump()
    )


@client_router.post(
        "/{microtik_slug}/create-client", 
        auth=GlobalAuth(permissions=[IsOwnerMicrotik, HasValidVpn]),
        response=list[ClientCreateResponse],
        description="La route pour le creation des clients par le owner microtik"
        )
def create_clients(request,data:ClientIn,microtik_slug:str):
    return ClientService.create_client_service(
        microtik=request.microtik,
        profil_slug=data.profil_slug,
        user_numbers=data.user_numbers
    )


@client_router.post(
        "/importe-csv", 
        response=list[ClientOut], 
        auth=GlobalAuth(permissions=[Auth,IsOwnerMicrotik])
        )
def import_csv(request, file: File[UploadedFile]):
    content = file.read().decode("utf-8")
    csv_data = io.StringIO(content)
    
    reader = csv.DictReader(csv_data)
    microtik = request.microtik
    return ClientService.csv_save_service(reader=reader, microtik=microtik)



@client_router.patch(
        "/{microtik_slug}/bloked-client/{user_slug}",
        auth=GlobalAuth(permissions=[IsOwnerMicrotik, HasValidVpn]),
        response=ClientBlockedOutSchemas,
        description="Le blocage d'un utilisateur."
        )
def block_client(request,user_slug:str,microtik_slug:str) -> ClientBlockedOutSchemas:

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        vpn = request.vpn,
        user_slug=user_slug,
        is_desable=True
    )


@client_router.patch(
        "/{microtik_slug}/unblok-client/{user_slug}",
        auth=GlobalAuth(permissions=[IsOwnerMicrotik, HasValidVpn]),
        description="la route pour le deblocage d'un client"
        )
def unblock_client(request,user_slug:str,microtik_slug:str) -> ClientBlockedOutSchemas:

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        vpn= request.vpn,
        user_slug=user_slug,
        is_desable=False
    )


@client_router.get(
        "{microtik_slug}/list-client",
        auth=GlobalAuth(permissions=[IsOwnerMicrotik]),
        response=list[ClientOut]
        )
def list_client(request,microtik_slug:str) -> list[ClientOut]:
    return ClientService.list_client_service(
        microtik=request.microtik,
        )


@client_router.get(
        "{microtik_slug}/retrieve-client/{client_slug}",
        auth=GlobalAuth(permissions=[IsOwnerMicrotik]),
        response=list[ClientRetrieve]
        )
def retrieve_client(request,client_slug:str,microtik_slug:str) -> list[ClientRetrieve]:
    return ClientService.retrieve_client_service(
        microtik=request.microtik,
        client_slug=client_slug,
        )


@client_router.get(
        "{microtik_slug}/actif-client",
        auth=GlobalAuth(permissions=[IsOwnerMicrotik, HasValidVpn]),
        response=list[ClientActifSchema]
        )
def actif_client(request,microtik_slug:str) -> list[ClientActifSchema]:
    return ClientService.actif_list_client_service(
        microtik=request.microtik,
        vpn=request.vpn
    )


@client_router.get(
        "{microtik_slug}/no-expired-client", 
        auth=GlobalAuth(permissions=[IsOwnerMicrotik, HasValidVpn]),
        response=list[ClientNoExpireSchema]
        )
def non_expire_client(request,microtik_slug:str) -> list[ClientNoExpireSchema]:
    return ClientService.no_expired_client_service(
        microtik=request.microtik
    )

