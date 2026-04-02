from ninja import Router

from app.clients.schemas import (
    InfoDepositIn,
    DepositResponseSchemas,
    PaymentWebhook
)
from app.clients.services import deposit, notif_url


client_router = Router(tags=["Client"])


@client_router.post("/deposit/{microtik_slug}", response=DepositResponseSchemas)
def deposit_client(request,data:InfoDepositIn, microtik_slug:str) -> DepositResponseSchemas:
    return deposit(microtik_slug=microtik_slug,data=data.model_dump())


@client_router.post("/notif/reponse/transaction/")
def notifiurl(request,data:PaymentWebhook):
    return notif_url(
        data=data.model_dump()
    )