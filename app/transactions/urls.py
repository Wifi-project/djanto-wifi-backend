from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from typing import Optional
from django.db.models import Q
from app.transactions.schemas import (
    TransactionOut,
    TransactionListOut,
    ResponseSchemas,
    )
from app.transactions.models import Transaction
from app.permissions.enum_permissions import PermissionsEnum
from app.permissions.checker import PermissionsChecker
from app.transactions.services import (
    list_subscriptions_for_network,
    log_transactions_for_owner_network,
    list_transaction_log,
    handle_transaction_webhook,
)

from app.transactions.models import PaymentMethod
from app.transactions.schemas import (
    PaymentMethodIn,
    PaymentMethodOut,
    PaymentMethodUpdate,
    TransactionOutIntransaction,
    TransactionVoucherListOut,
    WebhookPayload,
)

transactions = Router(tags=["Payment Methods"])


@transactions.get("/method/", response=List[PaymentMethodOut])
def list_payment_methods(request):
    return PaymentMethod.objects.filter(is_active=True)


@transactions.post("/method/", response={201: PaymentMethodOut})
def create_payment_method(request, payload: PaymentMethodIn):
    obj = PaymentMethod.objects.create(**payload.model_dump())
    return 201, obj


@transactions.get("/method/{slug}", response=PaymentMethodOut)
def get_payment_method(request, slug: str):
    return get_object_or_404(PaymentMethod, slug=slug)


@transactions.patch("/method/{slug}", response=PaymentMethodOut)
def update_payment_method(request, slug: str, payload: PaymentMethodUpdate):
    obj = get_object_or_404(PaymentMethod, slug=slug)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, attr, value)
    obj.save()
    return obj


# ── DELETE ───────────────────────────────────────────────────────────────────
@transactions.delete("/method/{slug}", response={204: None})
def delete_payment_method(request, slug: str):
    obj = get_object_or_404(PaymentMethod, slug=slug)
    obj.delete()
    return 204, None



#------------- Transaction pour le log ----------------------------



@transactions.get(
    "/transactions/",
    response=TransactionListOut,
    tags=['Logs transaction'],
    description="Liste paginée de toutes les transactions de la plateforme.",
)
def list_transactions(
    request,
    page_num:  int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search:    Optional[str] = Query(None, description="Recherche par transaction_id, phone, network_name"),
    status:    Optional[str] = Query(None, description="pending | completed | failed | cancelled"),
    type:      Optional[str] = Query(None, description="Type de transaction"),
):
    return list_transaction_log(
        search=search,
        status = status,
        page_num=page_num,
        page_size=page_size,
        type = type
    )


@transactions.get(
    "/transactions/{slug}/",
    tags=['Logs transaction'],
    response=TransactionOut,
    description="Détail d'une transaction.",
)
def retrieve_transaction(request, slug: str):
    transaction = get_object_or_404(
        Transaction.objects.select_related("network", "profil", "category"),
        slug=slug,
    )
    return transaction




#------------------- LES INFORMATIONS SUR LE PAIEMENT -----------------#
@transactions.get(
    "network/history/{network_slug}/",
    response=list[TransactionOut],
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_READ], owner=True),
    tags=["Logs transaction"],
    summary="Lister l'historique des paiements d'abonnements d'un reseau",
    description=(
        "Récupère la liste des paiements/abonnements associés à un reseau.\n\n"
        "**Permissions :**\n"
        "- Admin \n"
        "- Propriétaire "
    )
)
def get_subscriptions(request, network_slug: str) -> list[TransactionOut]:
    network = request.network
    return list_subscriptions_for_network(network=network)


@transactions.get(
    "/details/{slug}",
    response=TransactionOut,
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_READ]),
    tags=["Logs transaction"],
    summary="Obtenir un Paiement spécifique",
    description="Récupère les détails d'un paiement par son slug la route pour les admin pour les verifications."
)
async def get_subscription(request, slug: str) -> TransactionOut:
    ...
    # try:
    #     subscription = await Transaction.objects.aget(slug=slug)
    #     return subscription
    # except Transaction.DoesNotExist:
    #     raise HttpError(
    #         status_code=HTTPStatus.NOT_FOUND,
    #         message="Abonnement non trouvé"
    #     )


@transactions.get('/vouchers/log/{network_slug}/',
                tags=["Logs transaction"],
                response = TransactionVoucherListOut,
                auth=PermissionsChecker(permissions=[PermissionsEnum.DEPOSIT_READ], owner=True, has_subscription=True),
                description="Historique de payement des voucher pour un owner."
                )
def log_transaction(
    request,
    network_slug:str,
    page_num:  int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search:str='',
    status:str = ''):
    network = request.network 

    return log_transactions_for_owner_network(
        network=network,
        search = search,
        status = status,
        page_num = page_num,
        page_size = page_size
        )





#------------------ web hook -----------------------------------#


@transactions.post(
        "/webhook/transactions",
        tags=["webhook"],
        # response=ResponseSchemas,
        description="Le webhook pour le changement des status des transactions"
        )
def transaction_webhook(request: HttpRequest,data: WebhookPayload):
    
    signature_header = request.headers.get("X-Webhook-Signature")
    if not signature_header:
        return HttpResponse("Signature manquante", status=400)

    return handle_transaction_webhook(signature_header=signature_header, data=data.model_dump())
    