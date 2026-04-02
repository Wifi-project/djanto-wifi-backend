from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from app.users.deps import GlobalAuth

from app.admin_microtiks.schemas import (
    ClientIn,
    ClientCreateResponse,
    ClientOut,
    ClientActifSchema,
    ClientNoExpireSchema,
    ClientRetrieve,
    InfoDepositOut,
    InfoDepositRetrieve
)
from app.admin_microtiks.services import (
    create_users as create_user_service,
    list_user,
    actif_user_list,
    blocked_unlocked_user,
    users_no_expired,
    )


owner_microtik = Router(tags=["Owner_microtik"])

@owner_microtik.post("/{microtik_slug}/create-client", response=list[ClientCreateResponse])
def create_clients(request,data:ClientIn,microtik_slug:str):
    return create_user_service(
        microtik_slug=microtik_slug,
        profil_slug=data.profil_slug,
        user_numbers=data.user_numbers
    )


@owner_microtik.patch("/{microtik_slug}/bloked-client/{user_slug}")
def block_client(request,microtik_slug:str,user_slug:str):

    return blocked_unlocked_user(
        microtik_slug=microtik_slug,
        user_slug=user_slug,
        is_desable=True
    )


@owner_microtik.patch("/{microtik_slug}/unblok-client/{user_slug}")
def block_client(request,microtik_slug:str,user_slug:str):

    return blocked_unlocked_user(
        microtik_slug=microtik_slug,
        user_slug=user_slug,
        is_desable=False
    )


@owner_microtik.get("{microtik_slug}/list-client",response=list[ClientOut], auth=[GlobalAuth()])
def list_client(request,microtik_slug:str) -> list[ClientOut]:
    owner = request.user
    return list_user(microtik_slug=microtik_slug,owner=owner)


@owner_microtik.get("{microtik_slug}/actif-client",response=list[ClientActifSchema])
def actif_client(request,microtik_slug:str) -> list[ClientActifSchema]:
    return actif_user_list(
        microtik_slug=microtik_slug
    )


@owner_microtik.get("{microtik_slug}/no-expired-client", response=list[ClientNoExpireSchema])
def non_expire_client(request,microtik_slug:str) -> list[ClientNoExpireSchema]:
    return users_no_expired(
        microtik_slug=microtik_slug
    )
