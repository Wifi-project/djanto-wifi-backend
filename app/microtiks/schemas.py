from ninja.schema import Schema
from ninja import ModelSchema, Field
from app.microtiks.models import Microtik,Profil
from decimal import Decimal
from typing import List
from enum import Enum

class ProfilDuratinEnum(str,Enum):
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"

class StatusEnum(str,Enum):
    DISABLE = "disable"
    ACTIVE = "active"

class Cureency(str,Enum):
    GNF = "gnf"



class MikroTikRateLimit(str, Enum):
    BRONZE_MIN = "256k/512k"
    BRONZE_MAX = "512k/1M"
    SILVER_MIN = "1M/2M"
    SILVER_MAX = "2M/4M"
    GOLD_MIN = "4M/8M"
    GOLD_MAX = "5M/10M"
    PLATINUM = "10M/20M"
    ULTRA = "20M/50M"
    BUSINESS = "50M/100M"
    UNLIMITED = "0/0"

class CurrencyEnum(str, Enum):
    GNF = "gnf"


class ProfilBase(Schema):
    name: str
    rate_limit : MikroTikRateLimit 
    shared_users: int 
    price: Decimal
    currency: CurrencyEnum


class ProfilOutSchema(ProfilBase):
    slug:str

    class Config:
        from_attributes = True


class ProfilUpdateSchema(ProfilBase):
    name: str | None = None
    rate_limit : MikroTikRateLimit | None = None
    shared_users: int | None = None
    currency: str | None = None
    price: str | None = None
    status: StatusEnum | None = None
    type_session: ProfilDuratinEnum | None = None
    duration: int | None = None 


class ProfilInSchema(ProfilBase):
    status: StatusEnum | None = None
    type_session : ProfilDuratinEnum
    duration : int




class MicrotikInSchemas(ModelSchema):
    class Meta:
        model = Microtik
        fields = [
            "name",
            "description",
            "ip",
            "username",
            "password",
        ]

class MicrotikCheckSchemas(ModelSchema):
    class Meta:
        model = Microtik
        fields = [
            "ip",
            "username",
            "password",
        ]

class MicrotikCheckResponseSchemas(Schema):
    status: bool
    message: str


class MicrotikOutListSchemas(ModelSchema):
    class Meta:
        model = Microtik
        fields = [
            "slug",
            "name",
            "status"
        ]
        read_only_fields = fields


class MicrotikOutRetrieveSchemas(Schema):
    slug:str
    name: str
    description: str
    ip:str
    username: str 
    password: str
    status: StatusEnum
    sold: Decimal
    users: int 
    profils: List[ProfilOutSchema]
    
    class Config:
        from_attributes = True


# class MicrotikUpdateSchemas(ModelSchema):
#     class Meta:
#         model = Microtik
#         fields = [
#             "name",
#             "description",
#             "ip",
#             "username",
#             "password",
#             "status",
#         ]

class MicrotikUpdateSchemas(Schema):
    name:str | None = None
    description: str | None = None
    ip: str | None = None
    username: str | None = None
    password: str | None = None
    status: StatusEnum | None = None

