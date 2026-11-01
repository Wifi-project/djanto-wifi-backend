from ninja import Schema
from typing import Optional


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