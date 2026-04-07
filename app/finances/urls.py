from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination
from app.users.deps import GlobalAuth

from app.finances.schemas import (
    InfoDepositOut,
    InfoDepositRetrieve
)
from app.finances.services import (
    info_deposit_list,
    info_deposit_retrive
    )


finances_router = Router(
    tags=["Finances"],
    auth=[GlobalAuth()]
    )



#-------------------Infos deposit----------------------#

@finances_router.get(
        "/{microtik_slug} /list-deposit", 
        response=list[InfoDepositOut]
        )
def list_info_depost(request,microtik_slug:str) -> list[InfoDepositOut]:
    user = request.user
    return info_deposit_list(microtik_slug=microtik_slug,owner=user)


@finances_router.get(
        "/{microtik_slug}/retrieve/{deposit_slug}",
        response=list[InfoDepositRetrieve])
def retrieve_info_deposit(request,microtik_slug,deposit_slug):
    user = request.user
    return info_deposit_retrive(
        microtik_slug=microtik_slug,
        deposit_slug=deposit_slug,
        owner=user
    )


#--------------- 