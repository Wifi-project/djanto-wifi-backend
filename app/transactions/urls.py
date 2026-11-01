from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate

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