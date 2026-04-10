from ninja import ModelSchema, Field
from ninja.schema import Schema
from decimal import Decimal
from enum import Enum
from datetime import datetime
from pydantic import IPvAnyAddress


class SubscriptionCategoriEnum(str, Enum):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


#------------------Subscription Categorie abonement vpn ---------------#

class SubscriptionCategorieIntSchema(Schema):
    name: SubscriptionCategoriEnum
    price: Decimal | None = None
    is_active: bool


class SubscriptionCategorieUpdateSchema(Schema):
    name: SubscriptionCategoriEnum | None = None
    price: Decimal | None = None
    is_active: bool


class SubscriptionCategorieOutShema(Schema):
    slug: str | None = None
    name: SubscriptionCategoriEnum | None = None
    price: Decimal | None = None

    class Config:
        from_attributes = True



#-------------- Subscription ---------------#
class SubscriptionVpnInSchema(Schema):
    phone_number: str 
    amount: Decimal
    category_slug: str


class SubscriptionResponse(Schema):
    status: str 
    message: str 


class SubscriptionVpnOutSchema(Schema):
    vpn_username: str 
    vpn_password: str 
    vpn_ip: IPvAnyAddress | None = None
    expire_at: datetime | None = None
    is_paid: bool | None = None
    validation: bool | None = None
    category: SubscriptionCategorieOutShema | None = None

    class Config:
        from_attributes = True
