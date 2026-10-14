from ninja import Router
from ninja.pagination import paginate

from app.clients.schemas import (
    InfoDepositIn,
    DepositResponseSchemas,
    PaymentResponseSchema,
    PaymentWebhook,

    VoucherIn,
    VoucherGroupListResponseSchema,
    PaginatedResponseVoucherInGroupSchema,
    ClientPaginatedResponseSchema,
    SessionPaginatedResponseSchema,
    ClientBlockedOutSchemas
)
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum


from app.clients.services import (
    deposit,
    notif_url,
    ClientService,
    )

client_router = Router(tags=["Client"])


@client_router.post(
        "/deposit/{network_slug}/", 
        tags=["Achat-ticket"],
        response=DepositResponseSchemas)
async def deposit_client(request,data:InfoDepositIn, network_slug:str) -> DepositResponseSchemas:
    return await deposit(network_slug=network_slug,data=data.model_dump())


@client_router.post("/notif/reponse/transaction/",tags=["Achat-ticket"])
def notifiurl(request,data:PaymentWebhook):
    return notif_url(
        data=data.model_dump()
    )


@client_router.get(
        "{network_slug}/groups-voucher/",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_GROUP_READ],owner=True, has_subscription=True),
        response=list[VoucherGroupListResponseSchema],
        description="afficher la list des groupes de voucher"
)
async def list_group_voucher(request,network_slug:str,page_num:int=1,page_size:int=10,search:str=""):
    network= request.network

    return await ClientService.list_voucher_group_service(
        network=network,
        page_num=page_num,
        page_size=page_size,
        search=search
        )


@client_router.post(
        "/{network_slug}/create-voucher/", 
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, has_subscription=True),
        response=list[ClientBlockedOutSchemas],
        description="La route pour le creation des vouchers par le owner microtik"
        )
async def create_voucher(request,data:VoucherIn, network_slug:str):
    return await ClientService.create_voucher_service(
        network=request.network,
        profil_slug=data.profil_slug,
        voucher_number=data.voucher_number
    )


@client_router.get(
        "/{network_slug}/list-voucher-in-group/{group_id}/",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_READ], owner=True, has_subscription=True),
        response=PaginatedResponseVoucherInGroupSchema,
        description="la liste des vouchers dans le group"
        )
async def list_vouchers(request,group_id:str,search:str):
    network = request.network

    return await ClientService.list_voucher_in_group_service(
        network=network,
        group_id=group_id,
        search=search
    )


@client_router.delete(
        '/{network_slug}/delete-voucher/{voucher_id}',
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_DELETE], owner=True, has_subscription=True),
        response=ClientBlockedOutSchemas,
        description="supprimer un voucher"
        )
async def delete_voucher(request,network_slug,voucher_id):
    network = request.network

    return await ClientService.delete_voucher_service(
        network=network,
        voucher_id=voucher_id
    )


@client_router.delete(
        '/{network_slug}/delete-group-voucher/{group_id}',
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_GROUP_DELETE], owner=True, has_subscription=True),
        response=ClientBlockedOutSchemas,
        description="supprimer le group de voucher"
        )
async def delete_voucher(request,network_slug,voucher_id):
    network = request.network

    return await ClientService.delete_voucher_service(
        network=network,
        voucher_id=voucher_id
    )



#------------CLIENT-----------------------

@client_router.get(
        "/{network_slug}/list-clients",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_CREATE], owner=True, has_subscription=True),
        response=ClientPaginatedResponseSchema,
        description="la liste des client "
        )
async def list_clients(request,page_num:int,page_size:int,network_slug:str,start_at:int,end_at:int):
    network = request.network

    return await ClientService.list_client_service(
        network=network,
        page_size=page_size,
        page_num=page_num,
        start_at=start_at,
        end_at=end_at
    )



@client_router.patch(
        "/{network_slug}/bloked-client/{client_id}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_BLOCKED], owner=True, has_subscription=True),
        response=ClientBlockedOutSchemas,
        description="Le blocage d'un utilisateur."
        )
async def block_client(request,client_id:str,network_slug:str):

    return await ClientService.blocked_unlocked_client_service(
        network=request.network,
        client_id=client_id,
        enable=True
    )


@client_router.patch(
        "/{network_slug}/unblok-client/{client_id}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_UNBLOCKED], owner=True, has_subscription=True),
        description="la route pour le deblocage d'un client"
        )
async def unblock_client(request,client_id:str,network_slug:str):

    return await ClientService.blocked_unlocked_client_service(
        network=request.network,
        client_id=client_id,
        enable=False
    )



@client_router.get(
        "{network_slug}/actif-client",
        auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_READ], owner=True, has_subscription=True),
        response=list[SessionPaginatedResponseSchema]
        )
async def actif_client(request,network_slug:str,page_num:int,page_size:int):
    return await ClientService.actif_list_client_service(
        network=request.network,
        page_num=page_num,
        page_size=page_size
    )


# @client_router.get(
#         "{network_slug}/no-expired-client", 
#         auth=PermissionsChecker(permissions=[PermissionsEnum.CLIENT_READ], owner=True, has_subscription=True),
#         response=list[ClientNoExpireSchema]
#         )
# def non_expire_client(request,network_slug:str) -> list[ClientNoExpireSchema]:
#     return ClientService.no_expired_client_service(
#         microtik=request.microtik
#     )


