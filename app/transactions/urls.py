from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from typing import Optional
from django.db.models import Q
from app.utils.pagination import paginate_queryset
from app.transactions.schemas import TransactionOut, TransactionListOut
from app.transactions.models import Transaction



from app.transactions.models import PaymentMethod
from app.transactions.schemas import (
    PaymentMethodIn,
    PaymentMethodOut,
    PaymentMethodUpdate,
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
    qs = Transaction.objects.select_related("network", "profil", "category").order_by("-created_at")

    if search:
        qs = qs.filter(
            Q(transaction_id__icontains=search) |
            Q(phone_number__icontains=search)   |
            Q(network_name__icontains=search)
        )
    if status:
        qs = qs.filter(status=status)
    if type:
        qs = qs.filter(type=type)

    return paginate_queryset(qs, page_num, page_size)


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