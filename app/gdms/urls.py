from ninja import Router
from app.users.models import User
from ninja.pagination import paginate,LimitOffsetPagination
from typing import List
from app.gdms.models import Network,NetworkOwner,Gdms,Profil


from app.gdms.services import (
    check_network_name_service,
    create_network_service,
    list_network_service,
    retrive_network_service,
    update_network_service,
    delete_network_service,

    create_gdms_service,
    reboot_device_service,
    delete_device_service,
    ssid_update_service,
    block_ssid_service,
    unblock_ssid_service,
    isolation_ssid_service,

    create_owner_service,
    add_owner_service,
    remove_owner_service,

    create_profil_service,
    update_profil_service,
    delete_profil_service,
    profil_liste_service,

)

from app.gdms.schemas import (
    NetworkInSchemas,
    NetworkOutSchemas,
    NetworkRetrieveSchemas,
    CheckNetworkName,


    GdmsOutInNetwork,
    GdmsOutSchemas,
    GdmsInSchemas,
    GdmsRebootSchemas,
    GdmsDeviceBlockSchemas,

    ProfilOutSchema,
    ProfilUpdateSchema,
    ProfilInSchema,

    ResponseStatus
)

from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum
from app.users.schemas import (
    CreateOwnerSchemas,
    AddOwnerSchemas,

    )


gdms = Router(tags=["GDMS"], auth=[PermissionsChecker()])


#--------------------------GESTION NETWORK----------------------#
@gdms.post(
        "/network/create/",
        tags=["Network"],
        response=NetworkOutSchemas,
        auth=PermissionsChecker(permissions=[PermissionsEnum.NETWORK_CREATE]),
        description="La creation d'un network",
        )
async def create_network(request,data:NetworkInSchemas):
    user = request.user 
    return await create_network_service(data=data.model_dump(), user=user)


@gdms.patch(
        "/network/update/{network_slug}/",
        tags=["Network"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.NETWORK_UPDATE], owner=True, has_subscription=True),
        response=NetworkOutSchemas)
async def update_network(request,network_slug:str,data:NetworkInSchemas) -> Network:
    network = request.network
    return await update_network_service(data=data.model_dump(exclude_unset=True), network=network)


@gdms.post(
        "/check-network-name/", 
        tags=["Network"],
        response=ResponseStatus, 
        auth=PermissionsChecker(permissions=[]),
        description="verifier la disponibiliter d'un nom network"
        )
async def check_network_name(request,data:CheckNetworkName) -> dict[str,str] :
    return await check_network_name_service(name=data.name)


@gdms.get(
    "/network/list/", 
    tags=["Network"],
    response=list[NetworkOutSchemas],
    description="afficher la liste des network de user connecter et tous les networks pour un admin",
    auth=[PermissionsChecker(permissions=[PermissionsEnum.NETWORK_READ])]  
)
@paginate(LimitOffsetPagination, papage_size=10)
def list_network(request) -> list[Network]:
    user = request.user   
    return list_network_service(user = user)


@gdms.get(
        "/network/retrieve/{network_slug}", 
        response=NetworkRetrieveSchemas, 
        auth=PermissionsChecker(permissions=[PermissionsEnum.NETWORK_READ],owner=True, has_subscription=True),
        tags=["Network"],
        description="afficher detail d'un reseau network,")
def retrieve_network(request, network_slug):
    user = request.user
    if user.user_type == User.ADMIN:
        network = Network.objects.filter(slug=network_slug).first()
    else:
        network = Network.objects.filter(slug=network_slug,owners=user).first()
    return network



@gdms.delete(
        "/network/delete/{network_slug}/", 
        tags=["Network"],
        response=ResponseStatus,
        auth=PermissionsChecker(permissions=[PermissionsEnum.NETWORK_DELETE], owner=True, has_subscription=True),
        description="supprimer un network"
        )
async def delete_network(request,network_slug:str) -> dict[str,str]:
    network = request.network
    return await delete_network_service(network=network)




#------------------------GESTION GDMS---------------------------------#

@gdms.post(
        "/gdms/device/create/{network_slug}/", 
        tags=["GDMS"],
        response=GdmsOutSchemas,
        auth=PermissionsChecker(permissions=[PermissionsEnum.GDMS_CREATE], owner=True, has_subscription=True),
        description="cree un gdms."
        )
async def create_gdms(request,network_slug:str, data:GdmsInSchemas) -> Gdms:
    network = request.network
    user = request.user
    return await create_gdms_service(
        network=network,
        data=data.model_dump(),
        user=user
        )


@gdms.post(
        "/gdms/device/reboot/{network_slug}/", 
        tags=["GDMS"],
        response=ResponseStatus,
        auth=PermissionsChecker(permissions=[PermissionsEnum.GDMS_UPDATE], owner=True, has_subscription=True),
        description="cree un gdms."
        )
async def reboot_gdms(request,network_slug:str, data:GdmsRebootSchemas) -> dict[str,str]:
    network = request.network
    return await reboot_device_service(network=network,data=data.model_dump(),)


@gdms.delete(
        '/gdms/device/delete/{network_slug}/',
        tags=['GDMS'],
        response=ResponseStatus,
        auth=PermissionsChecker(permissions=[PermissionsEnum.GDMS_DELETE], owner=True, has_subscription=True),
        description="supprimer un device"
)
async def delete_device(request,network_slug:str,data:GdmsRebootSchemas) -> dict[str,str]:

    return await delete_device_service(data.model_dump())


@gdms.patch(
        '/gdms/ssid/block/{network_slug}/',
        tags=['GDMS'],
        response=ResponseStatus,
        auth=PermissionsChecker(permissions=[PermissionsEnum.SSID_BLOCK], owner=True, has_subscription=True),
        description="bloquer un device "
)
async def block_ssid(request,network_slug:str, data:GdmsDeviceBlockSchemas) -> dict[str,str]:
    network = request.network
    data_dict = data.model_dump()

    return await block_ssid_service(
        network=network,
        gdms_slug=data_dict.get('gdms_slug')
        )


@gdms.patch(
        '/gdms/ssid/unblock/{network_slug}/',
        tags=['GDMS'],
        response=ResponseStatus,
        auth=PermissionsChecker(permissions=[PermissionsEnum.SSID_UNLOCK], owner=True, has_subscription=True),
        description="debloquer un device"
)
async def unblock_ssid(request,network_slug:str, data:GdmsDeviceBlockSchemas) -> dict[str,str]:
    network = request.network
    data_dict = data.model_dump()

    return await unblock_ssid_service(
        network=network,
        gdms_slug=data_dict.get('gdms_slug')
        )


@gdms.post(
    '/gdms/ssid/isolation/{network_slug}/',
    tags=['GDMS'],
    response=ResponseStatus,
    auth=PermissionsChecker(
        permissions=[PermissionsEnum.GDMS_UPDATE],
        owner=True,
        has_subscription=True,
    ),
    description="appliquer l'isolation"
)
async def ssid_isolation(request,network_slug:str, data: GdmsDeviceBlockSchemas) -> dict[str, str]:
    network = request.network
    gdms_slug = data.model_dump()

    return await isolation_ssid_service(
        network=network,
        gdms_slug=gdms_slug.get('gdms_slug'),
    )


# @gdms.patch(
#         '/gdms/ssid/update/{network_slug}/',
#         tags=['GDMS'],
#         response=GdmsOutSchemas,
#         description="faire la mise a jours d'un ssid gdms"
# )
# async def update_device(request) -> Gdms:
#     await ssid_update_service()




#------------------------------LES PROFILES -------------------------------#

@gdms.post(
        '/{network_slug}/profile-create/', 
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_CREATE], owner=True, has_subscription=True),
        response=ProfilOutSchema, 
        description="creation des profil pour un microtik"
        )
def profile_create(request,data:ProfilInSchema, network_slug:str) -> Profil:
    network = request.network

    return create_profil_service(
        data=data.model_dump(),
        network=network
        )


@gdms.patch(
        '/{network_slug}/update-profile/{slug_profil}/', 
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_UPDATE], owner=True, has_subscription=True),
        response=ProfilOutSchema,
        description="La mise a jour du profile microtik"
        )
def profile_update(request,data:ProfilUpdateSchema,slug_profil:str,network_slug:str) -> Profil:

    return update_profil_service(
        network=request.network,
        slug_profil=slug_profil, 
        data=data.model_dump(exclude_unset=True)
        )


@gdms.delete(
        '/{network_slug}/delete-profil/{slug_profil}/',
        tags=["Routeurs Profile"],
        auth=PermissionsChecker(permissions=[PermissionsEnum.PROFIL_DELETE], owner=True, has_subscription=True),
        response=ProfilOutSchema,
        description="Supprimer un profil"
        )
def delete_profil(request,slug_profil:str,network_slug:str) -> Profil:

    return delete_profil_service(
        network_slug=request.network,
        profil_slug=slug_profil,
    )


@gdms.get(
        '/{network_slug}/list-profil/', 
        tags=["Routeurs Profile"],
        response= List[ProfilOutSchema],
        description="Afficher la liste des proles d'un microtik.",
        auth=None
        )
def list_profil(request,network_slug:str):
    # user = request.user 
    return profil_liste_service(
        network_slug=network_slug
        )




#-------------------------GESTION DES OWNERS ----------------------------------#

@gdms.post(
        "{network_slug}/owner/create/",
        tags=["Gestionnaire Network"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def create_owner(request,data:CreateOwnerSchemas,network_slug:str):
    network = request.network
    return create_owner_service(
        network=network,
        owner_data=data.model_dump()
        )


@gdms.post(
        "{network_slug}/owner/add/",
        tags=["Gestionnaire Network"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def add_owner(request,network_slug:str,data:AddOwnerSchemas):
    network = request.network
    return add_owner_service(
        network=network,
        email=data.email
    )


@gdms.patch(
        "{network_slug}/owner/remove/",
        tags=["Gestionnaire Network"],
        auth=[PermissionsChecker(permissions=[], owner=True)]
        )
def remove_owner(request,network_slug:str,data:AddOwnerSchemas):
    network = request.network

    return remove_owner_service(
        user_slug=data.email,
        network=network
    )


# @gdms.post(
#         "{microtik_slug}/owner/add-group/{slug_group}/",
#         tags=["Gestionnaire Routeurs"],
#         auth=[PermissionsChecker(permissions=[], owner=True)]
#         )
# def add_owner_group(request,microtik_slug:str,data:AddOwnerGroup,slug_group:str):
#     microtik = request.microtik
#     return add_owner_group_service(
#         microtik=microtik,
#         slug_user=data.slug_user,
#         slug_group=slug_group
#     )


# @gdms.patch(
#         "{microtik_slug}/owner/remove-group/{slug_group}/",
#         tags=["Gestionnaire Routeurs"],
#         auth=[PermissionsChecker(permissions=[], owner=True)]
#         )
# def remove_group(request,data:AddOwnerGroup, microtik_slug:str,slug_group:str):
#     microtik = request.microtik
#     return remove_owner_group_service(
#         microtik=microtik,
#         slug=data.slug_user,
#         slug_group=slug_group
#     )





