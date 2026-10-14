from ninja.schema import Schema
from ninja import ModelSchema, Field
from app.gdms.models import Gdms
from decimal import Decimal
from typing import List
from enum import Enum
from app.users.schemas import UserOwnerOutSchema
from app.permissions.schemas import PermissionGroupsList
from datetime import date


class ProfilDuratinEnum(str,Enum):
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"

class StatusEnum(str,Enum):
    DISABLE = "disable"
    ACTIVE = "active"

class Cureency(str,Enum):
    GNF = "gnf"



class NetworkRateLimit(str, Enum):
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

#------------------PROFIL------------------#

class ProfilBase(Schema):
    name: str
    rate_limit : NetworkRateLimit 
    shared_users: int 
    price: Decimal
    currency: CurrencyEnum


class ProfilOutSchema(ProfilBase):
    slug:str

    class Config:
        from_attributes = True


class ProfilUpdateSchema(ProfilBase):
    name: str | None = None
    rate_limit : NetworkRateLimit | None = None
    shared_users: int | None = None
    currency: str | None = None
    price: str | None = None
    type_session: ProfilDuratinEnum | None = None
    duration: int | None = None 


class ProfilInSchema(ProfilBase):
    type_session : ProfilDuratinEnum
    duration : int



#--------------Network------------------#

class NetworkInSchemas(Schema):
    name: str
    description:str


from pydantic import ConfigDict

class NetworkOutSchemas(Schema):
    slug: str
    name: str
    description: str
    status: StatusEnum | None = None

    model_config = ConfigDict(from_attributes=True)
    

class NetworkRetrieveSchemas(Schema):
    slug: str
    name: str
    description: str | None = None
    network_id: int | str | None = None
    commission_rate: Decimal
    wallet_balance: Decimal
    admin_blocked: bool
    subscription_expire_at: date | None = None
    subscription: bool
    days_remaining: int
    gdms_network: list['GdmsOutInNetwork'] = []
    profils: list['ProfilOutSchema'] = []
    network_owners: list['OwnerNetworkOutInNetworkSchemas'] = []

    model_config = ConfigDict(from_attributes=True)


class CheckNetworkName(Schema):
    name: str


#----------------Owner network-----------------#

class OwnerNetworkOutInNetworkSchemas(Schema):
    user: UserOwnerOutSchema
    group_permissions: list[PermissionGroupsList] = []

    model_config = ConfigDict(from_attributes=True)

#-----------------Gdms---------------------#
class GdmsBaseSchema(Schema):
    slug: str
    description: str
    gdms_site_id: str 
    mac_address: str 
    serial_number: str 
    is_online: bool
    status: StatusEnum

    class Config: 
        from_attributes = True


class GdmsOutInNetwork(GdmsBaseSchema):
    ...


class GdmsOutSchemas(GdmsBaseSchema):
    network : NetworkOutSchemas



class GdmsInSchemas(Schema):
    mac: str 
    password: str
    description: str 
    # newtwork_slug: str


class GdmsRebootSchemas(Schema):
    mac: list[str]


class GdmsDeviceBlockSchemas(Schema):
    gdms_slug: str

class ResponseStatus(Schema):
    status: str
    message: str