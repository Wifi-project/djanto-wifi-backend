from ninja import Schema
from typing import Optional
from datetime import datetime
from decimal import Decimal
from typing import Optional
from ninja import Schema

class PaymentMethodIn(Schema):
    name: str
    code: str


class PaymentMethodOut(Schema):
    slug: str
    name: str
    code: str


class PaymentMethodUpdate(Schema):
    name: Optional[str] = None
    code: Optional[str] = None



#__________TRANSACTION____________


class TransactionOut(Schema):
    slug: str
    transaction_id: Optional[str] = None
    phone_number: Optional[str] = None
    amount: Decimal
    network_name: Optional[str] = None
    network_description: Optional[str] = None
    payment_method: str
    type: str
    status: str
    created_at: Optional[datetime] = None

    # @staticmethod
    # def resolve_network_slug(obj):
    #     return obj.network.slug if obj.network else None

    # @staticmethod
    # def resolve_profil_name(obj):
    #     return obj.profil.name if obj.profil else None

    # @staticmethod
    # def resolve_category_name(obj):
    #     return obj.category.name if obj.category else None


class TransactionListOut(Schema):
    result: list[TransactionOut]
    total: int
    totalPage: int
    currentPage: int