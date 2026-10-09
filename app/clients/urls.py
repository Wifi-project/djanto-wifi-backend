from ninja import Router, File
import csv
import io
from ninja.files import UploadedFile
from ninja.pagination import paginate

from app.clients.schemas import (
    InfoDepositIn,
    DepositResponseSchemas,
    PaymentResponseSchema,
    PaymentWebhook,
    VoucherIn,
    VoucherCreateResponse,
    GroupClientOutSchema,
    ClientOut,
    ClientActifSchema,
    ClientNoExpireSchema,
    ClientBlockedOutSchemas,
    ClientRetrieve,
)
from app.users.deps import GlobalAuth,IsOwnerMicrotik,HasValidVpn,Auth
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum


from app.clients.services import (
    deposit,
    notif_url,
    ClientService,
    )

client_router = Router(tags=["Client"])


@client_router.post(
        "/deposit/{microtik_slug}", 
        tags=["Achat-ticket"],
        response=DepositResponseSchemas)
async def deposit_client(request,data:InfoDepositIn, microtik_slug:str) -> DepositResponseSchemas:
    return await deposit(microtik_slug=microtik_slug,data=data.model_dump())


@client_router.post("/notif/reponse/transaction/",tags=["Achat-ticket"])
def notifiurl(request,data:PaymentWebhook):
    return notif_url(
        data=data.model_dump()
    )


@client_router.get(
        "{microtik_slug}/group-voucher",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_GROUP],owner=True),
        response=list[GroupClientOutSchema]
)
@paginate
def list_group_voucher(request,microtik_slug:str):
    return ClientService.list_group(microtik=request.microtik)


@client_router.post(
        "/{microtik_slug}/create-voucher", 
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, hasWG=True),
        response=list[VoucherCreateResponse],
        description="La route pour le creation des vouchers par le owner microtik"
        )
def create_voucher(request,data:VoucherIn, microtik_slug:str):
    return ClientService.create_voucher_service(
        microtik=request.microtik,
        profil_slug=data.profil_slug,
        voucher_number=data.voucher_number
    )


@client_router.get(
        "/{microtik_slug}/list-voucher",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, hasWG=True),
        )
def list_voucher(request,page_num:int,page_size:int,microtik_slug:str):
    microtik = request.microtik
    subscription = request.subscription

    return ClientService.list_voucher_service(
        microtik=microtik,
        subscription=subscription,
        page_size=page_size,
        page_num=page_num
    )

@client_router.delete(
        '/{microtik_slug}/delete_voucher/{voucher_id}',
        auth=PermissionsChecker(permissions=[PermissionsEnum.CATEGORY_DELETE], owner=True, hasWG=True),
        )
def delete_voucher(request,microtik_slug,voucher_id):
    microtik = request.microtik
    subscription = request.subscription

    return ClientService.delete_voucher_service(
        microtik=microtik,
        subscription=subscription,
        voucher_id=voucher_id
    )


@client_router.get(
        "/{microtik_slug}/list-clients",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, hasWG=True),
        )
def list_clients(request,page_num:int,page_size:int,microtik_slug:str):
    microtik = request.microtik
    subscription = request.subscription

    return ClientService.list_client_service(
        microtik=microtik,
        subscription=subscription,
        page_size=page_size,
        page_num=page_num
    )


@client_router.get(
        "/{microtik_slug}/retrieve-client/{client_id}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, hasWG=True),
        )
def retrieve_clients(request,client_id:int,microtik_slug:str):
    microtik = request.microtik
    subscription = request.subscription

    return ClientService.retrieve_client_service(
        microtik=microtik,
        subscription=subscription,
        client_id=client_id
    )


@client_router.patch(
        "/{microtik_slug}/bloked-client/{client_id}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_BLOCKED], owner=True, hasWG=True),
        # response=ClientBlockedOutSchemas,
        description="Le blocage d'un utilisateur."
        )
def block_client(request,client_id:str,microtik_slug:str):

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        client_id=client_id,
        subscription=request.subscription,
        enable=True
    )


@client_router.patch(
        "/{microtik_slug}/unblok-client/{client_id}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_UNBLOCKED], owner=True, hasWG=True),
        description="la route pour le deblocage d'un client"
        )
def unblock_client(request,client_id:str,microtik_slug:str):

    return ClientService.blocked_unlocked_client_service(
        microtik=request.microtik,
        client_id=client_id,
        subscription=request.subscription,
        enable=False
    )



@client_router.get(
        "{microtik_slug}/actif-client",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_READ], owner=True, hasWG=True),
        # response=list[ClientActifSchema]
        )
def actif_client(request,microtik_slug:str,page_num:int,page_size:int):
    return ClientService.actif_list_client_service(
        microtik=request.microtik,
        subscription=request.subscription,
        page_num=page_num,
        page_size=page_size
    )


# @client_router.get(
#         "{microtik_slug}/no-expired-client", 
#         auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_READ], owner=True, hasWG=True),
#         response=list[ClientNoExpireSchema]
#         )
# def non_expire_client(request,microtik_slug:str) -> list[ClientNoExpireSchema]:
#     return ClientService.no_expired_client_service(
#         microtik=request.microtik
#     )



# @client_router.post(
#         "/importe-csv", 
#         response=list[ClientOut], 
#         auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, hasWG=True),
#         )
# def import_csv(request, file: File[UploadedFile]):
#     content = file.read().decode("utf-8")
#     csv_data = io.StringIO(content)
    
#     reader = csv.DictReader(csv_data)
#     microtik = request.microtik
#     return ClientService.csv_save_service(reader=reader, microtik=microtik)
