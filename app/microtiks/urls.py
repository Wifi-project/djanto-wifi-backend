from ninja import Router
from app.users.models import User
from ninja.pagination import paginate,LimitOffsetPagination
from typing import List
from app.microtiks.models import Microtik
from app.microtiks.services import (
    create_microtik_service,
    update_microtik_service,
    check_connexion as check_connexion_service,
    create_profil_service,
    update_profil_service,
    delete_profil_service as delete,
    profil_liste_service,
    updateInfosSubscriptionWg,
    retrieve_microtik_service,

    create_owner_service,
    add_owner_service,
    remove_owner_service,
    add_owner_group_service,
    remove_owner_group_service,
)
from app.microtiks.schemas import (
    MicrotikInSchemas,
    MicrotikOutListSchemas,
    MicrotikOutRetrieveSchemas,
    MicrotikUpdateSchemas,
    MicrotikCheckResponseSchemas,
    ProfilInSchema,
    ProfilOutSchema,
    ProfilUpdateSchema,

    AddOwnerGroup
)
from app.subscriptions.schemas import (AddInformationMicrotik,SubscriptionWGBaseSchema)
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum
from app.users.schemas import (
    CreateOwnerSchemas,
    AddOwnerSchemas,

    )


microtik_router = Router(tags=["Routeurs"], auth=[PermissionsChecker()])


#--------------------------GESTION MICROTIK----------------------#
@microtik_router.post(
        "/create",
        tags=["Routeurs"],
        response=MicrotikOutListSchemas,
        auth=PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_CREATE]),
        description="La creation d'un microtik",
        )
def create(request,data:MicrotikInSchemas):
    user = request.user 
    return create_microtik_service(data=data.model_dump(), user=user)


@microtik_router.patch(
        "/update-access/{microtik_slug}",
        tags=['Routeurs'],
        auth=PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_UPDATE], owner=True, hasWG=True),
        response=SubscriptionWGBaseSchema)
def update_access(request,microtik_slug:str,data:AddInformationMicrotik) -> SubscriptionWGBaseSchema:
    microtik = request.microtik
    return updateInfosSubscriptionWg(data=data.model_dump(), microtik=microtik)


@microtik_router.post(
        "/check-connexion/{microtik_slug}", 
        tags=["Routeurs"],
        response=MicrotikCheckResponseSchemas, 
        auth=PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_READ], owner=True,hasWG=True),
        description="Verifier la connexion avec le microtik voir si les infos saisies sont exactent"
        )
def check_connexion(request,microtik_slug:str) -> MicrotikCheckResponseSchemas:
    microtik = request.microtik
    return check_connexion_service(microtik=microtik)


@microtik_router.patch(
    "/update/{microtik_slug}", 
    tags=["Routeurs"],
    response=MicrotikOutListSchemas,
    description="Modifier un microtik",
    auth=[PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_UPDATE], owner=True)]  
)
def update(request, data: MicrotikUpdateSchemas, microtik_slug: str) -> MicrotikOutListSchemas:
    user = request.user   
    microtik = request.microtik
    return update_microtik_service(
        data=data.model_dump(exclude_unset=True), 
        user = user,
        microtik=microtik)


@microtik_router.get(
        "/list/", 
        response=list[MicrotikOutListSchemas], 
        auth=PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_READ]),
        tags=["Routeurs"],
        description="afficher la liste des microtiks appartenant a la personne connecter," \
        "si la personne connecter est un admin il verra la liste de tous les microtiks existant."
        )
@paginate(LimitOffsetPagination, papage_size=10)
def list_microtik(request):
    user = request.user
    if user.user_type == User.ADMIN:
        microtik = Microtik.objects.all()
    else:
        microtik = Microtik.objects.filter(owners=user)
    return microtik



@microtik_router.get(
        "/retrieve/{microtik_slug}/", 
        tags=["Routeurs"],
        response=MicrotikOutRetrieveSchemas,
        auth=PermissionsChecker(permissions=[PermissionsEnum.MICROTIK_READ], owner=True),
        description="afficher les details d'un microtik."
        )
def retrieve_microtik(request,microtik_slug:str) -> MicrotikOutRetrieveSchemas:
    return request.microtik



#------------------------------LES PROFILES -------------------------------#

@microtik_router.post(
        '/{microtik_slug}/profile-create/', 
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_CREATE], owner=True, hasWG=True),
        response=MicrotikCheckResponseSchemas, 
        description="creation des profil pour un microtik"
        )
def profile_create(request,data:ProfilInSchema, microtik_slug:str) -> MicrotikCheckResponseSchemas:
    microtik = request.microtik

    return create_profil_service(
        data=data.model_dump(),
        microtik=microtik
        )


@microtik_router.patch(
        '/{microtik_slug}/update-profile/{slug_profil}/', 
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_UPDATE], owner=True, hasWG=True),
        response=MicrotikCheckResponseSchemas,
        description="La mise a jour du profile microtik"
        )
def profile_update(request,data:ProfilUpdateSchema,slug_profil:str,microtik_slug:str) -> MicrotikCheckResponseSchemas:

    return update_profil_service(
        microtik=request.microtik,
        slug_profil=slug_profil, 
        data=data.model_dump(exclude_unset=True)
        )


@microtik_router.delete(
        '/{microtik_slug}/delete-profil/{slug_profil}/',
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_DELETE], owner=True, hasWG=True),
        response=MicrotikCheckResponseSchemas,
        description="Supprimer un profil"
        )
def delete_profil(request,slug_profil:str,microtik_slug:str) -> MicrotikCheckResponseSchemas:

    return delete(
        microtik_slug=request.microtik,
        profil_slug=slug_profil,
    )


@microtik_router.get(
        '/{microtik_slug}/list-profil/', 
        tags=["Routeurs Profile"],
        response= List[ProfilOutSchema],
        description="Afficher la liste des proles d'un microtik.",
        auth=None
        )
def list_profil(request,microtik_slug:str):
    # user = request.user 
    return profil_liste_service(
        microtik_slug=microtik_slug
        )


#-------------------------GESTION DES OWNERS ----------------------------------#

@microtik_router.post(
        "{microtik_slug}/owner/create/",
        tags=["Gestionnaire Routeurs"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def create_owner(request,data:CreateOwnerSchemas,microtik_slug:str):
    microtik = request.microtik
    return create_owner_service(
        microtik=microtik,
        owner_data=data.model_dump()
        )


@microtik_router.post(
        "{microtik_slug}/owner/add/",
        tags=["Gestionnaire Routeurs"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def add_owner(request,microtik_slug:str,data:AddOwnerSchemas):
    microtik = request.microtik
    return add_owner_service(
        microtik=microtik,
        email=data.email
    )


@microtik_router.post(
        "{microtik_slug}/owner/add-group/{slug_group}/",
        tags=["Gestionnaire Routeurs"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def add_owner_group(request,microtik_slug:str,data:AddOwnerGroup,slug_group:str):
    microtik = request.microtik
    return add_owner_group_service(
        microtik=microtik,
        slug_user=data.slug_user,
        slug_group=slug_group
    )


@microtik_router.patch(
        "{microtik_slug}/owner/remove/",
        tags=["Gestionnaire Routeurs"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def remove_owner(request,microtik_slug:str,data:AddOwnerGroup):
    microtik = request.microtik

    return remove_owner_service(
        slug=data.slug_user,
        microtik=microtik
    )


@microtik_router.patch(
        "{microtik_slug}/owner/remove-group/{slug_group}/",
        tags=["Gestionnaire Routeurs"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def remove_group(request,data:AddOwnerGroup, microtik_slug:str,slug_group:str):
    microtik = request.microtik
    return remove_owner_group_service(
        microtik=microtik,
        slug=data.slug_user,
        slug_group=slug_group
    )





# from ninja import Router, Schema
# from app.models import NetworkDevice, Voucher, VoucherStatus
# from services.gdms_driver import GdmsCloudDriver

# router = Router()

# class GenerateVoucherSchema(Schema):
#     device_id: int
#     duration_minutes: int # Ex: 60 pour 1h, 1440 pour 24h

# # 1. Endpoint pour générer un ticket après achat
# @router.post("/vouchers/generate")
# def create_user_voucher(request, payload: GenerateVoucherSchema):
#     device = NetworkDevice.objects.get(id=payload.device_id, organization__owner=request.user)
#     driver = GdmsCloudDriver()

#     res = driver.generate_vouchers(
#         site_id=device.gdms_site_id,
#         duration_minutes=payload.duration_minutes,
#         count=1
#     )

#     if not res.is_success:
#         return {"status": "error", "message": res.message}, 400

#     raw_voucher = res.data["vouchers"][0]
    
#     # Enregistrement en BDD local
#     voucher = Voucher.objects.create(
#         device=device,
#         code=raw_voucher["code"],
#         gdms_voucher_id=str(raw_voucher["voucherId"]),
#         duration_minutes=payload.duration_minutes,
#         status=VoucherStatus.UNUSED
#     )

#     return {
#         "status": "success",
#         "code": voucher.code,
#         "duration_minutes": voucher.duration_minutes
#     }

# # 2. Endpoint pour Bloquer / Débloquer un ticket
# @router.post("/vouchers/{voucher_id}/toggle-block")
# def toggle_block_voucher(request, voucher_id: int, block: bool):
#     voucher = Voucher.objects.get(id=voucher_id, device__organization__owner=request.user)
#     driver = GdmsCloudDriver()

#     res = driver.set_voucher_block_status(
#         site_id=voucher.device.gdms_site_id,
#         voucher_id=voucher.gdms_voucher_id,
#         is_blocked=block
#     )

#     if res.is_success:
#         voucher.status = VoucherStatus.BLOCKED if block else VoucherStatus.UNUSED
#         voucher.save()
#         return {"status": "success", "message": res.message}
    
#     return {"status": "error", "message": res.message}, 400