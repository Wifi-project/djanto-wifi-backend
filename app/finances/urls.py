from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum

from app.finances.schemas import (
    InfoDepositOut,
    InfoDepositRetrieve,
    WindrawSchemas,
    ResponseWindrawSchemas,
    WindrawBaseSchema,
    WindrawOutSchema
)
from app.finances.services import (
    info_deposit_list,
    info_deposit_retrive,
    windraw_service,
    historique_windraw_service,
    windraw_retrieve_service
    )


finances_router = Router(
    tags=["Finances"],
    auth=[PermissionsChecker()]
    )



#-------------------Infos deposit----------------------#

@finances_router.get(
        "/{microtik_slug}/list-deposit", 
        auth=PermissionsChecker(permissions=[PermissionsEnum.DEPOSIT_READ], owner=True),
        summary="La liste des depots effectuer par les clients pour achat des tickets",
        response=list[InfoDepositOut]
        )
def list_info_depost(request,microtik_slug:str) -> list[InfoDepositOut]:
    # user = request.user
    return info_deposit_list(
        microtik=request.microtik
        )


@finances_router.get(
        "/{microtik_slug}/retrieve/{deposit_slug}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.DEPOSIT_READ], owner=True),
        summary="Le detail d'un depot effectuer par un client",
        response=InfoDepositRetrieve)
def retrieve_info_deposit(request,microtik_slug:str,deposit_slug:str) -> InfoDepositRetrieve:
    return info_deposit_retrive(
        microtik=request.microtik,
        deposit_slug=deposit_slug,
    )


#--------------- Windrawal ----------------

@finances_router.post(
        "/windraw/init/{microtik_slug}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.FINANCE_REQUEST_WITHDRAW],owner=True),
        summary="Initier un retrait de son argent",
        response=ResponseWindrawSchemas)
def windraw_init(request,microtik_slug:str, data:WindrawSchemas) -> ResponseWindrawSchemas:
    return windraw_service(
        microtik=request.microtik,
        user = request.user,
        data = data.model_dump()
    )


@finances_router.get(
    "/windraw/histoique/{microtik_slug}",
    response=list[WindrawBaseSchema],
    auth=PermissionsChecker(permissions=[PermissionsEnum.FINANCE_READ_ALL_WITHDRAW], owner=True),
    summary="Voir l'historique de ses retraits par microtik."
    )
def windraw_historique(request, microtik_slug:str, status:str | None = None,reference:str| None = None) -> WindrawBaseSchema:
    return historique_windraw_service(
        microtik = request.microtik,
        status=status,
        reference=reference
    )


@finances_router.get(
    "/windraw/{microtik_slug}/retrieve/{windraw_slug}",
    response=WindrawOutSchema,
    summary="Le detail d'un retrait",
    auth=PermissionsChecker(permissions=[PermissionsEnum.FINANCE_READ_WITHDRAW], owner=True),
)
def retrieve_windraw(request,microtik_slug:str,windraw_slug:str):
    return windraw_retrieve_service(
        microtik=request.microtik,
        slug = windraw_slug
    )


@finances_router.patch(
        "/windraw/{microtik_slug}/cancel/{windraw_slug}",
        response=ResponseWindrawSchemas,
        summary="Annuler une demande de retrait",
    auth=PermissionsChecker(permissions=[PermissionsEnum.FINANCE_CANCEL_WITHDRAW], owner=True),
        )
def windraw_cancel(request,microtik_slug:str, windraw_slug:str):
    return 