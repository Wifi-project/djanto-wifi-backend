from ninja.schema import Schema
from ninja import ModelSchema, Field
from app.gdms.models import Gdms
from decimal import Decimal
from typing import List
from enum import Enum
from app.users.schemas import UserOwnerOutSchema
from app.permissions.schemas import PermissionGroupsList
from datetime import date
from app.subscriptions.schemas import ConfigurationInSchema


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

class NetworkBaseCreateSchemas(Schema):
    name: str
    description: str
    
class NetworkInSchemas(Schema):
    network: NetworkBaseCreateSchemas
    configuration: ConfigurationInSchema


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
    site_id: str | None = None
    set_isloation: bool
    commission_rate: Decimal
    wallet_balance: Decimal
    admin_blocked: bool
    subscription_expire_at: date | None = None
    subscription: bool
    days_remaining: int
    configuration_paid:bool
    status: str
    gdms_network: list['GdmsOutInNetwork'] = []
    profils: list['ProfilOutSchema'] = []
    network_owners: list['OwnerNetworkOutInNetworkSchemas'] = []

    model_config = ConfigDict(from_attributes=True)


class CheckNetworkName(Schema):
    name: str


#----------------Owner network-----------------#

class OwnerNetworkOutInNetworkSchemas(Schema):
    user: UserOwnerOutSchema | None = None
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
    description: str | None = None
    serial_number: str | None = None
    gdms_site_id: str | None = None
    mac_address: str | None = None


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

class SsiIsolationSchemas(Schema):
    isolation: bool

class ResponseStatus(Schema):
    status: str
    message: str


#---------------- SSID -----------------------
class SsidOutSchema(Schema):
    """Un SSID (réseau WiFi) tel que retourné par l'API."""
    id: int
    ssidName: str
    ssidRemark: str | None = None
    wifiEnabled: int          # 0 ou 1
    vlanId: str | None = None
    onlineDevices: int
    scheduleEnabled: int
    portalEnabled: int
    securityMode: int
    macFilteringEnabled: int
    clientIsolationEnabled: int


class SsidListOutSchema(Schema):
    """Réponse paginée de la liste des SSIDs."""
    result: list[SsidOutSchema]
    total: int
    pages: int
    pageSize: int
    pageNum: int


#------------- DEVICE ------------------------

class ApOutSchema(Schema):
    """Un point d'accès (AP) tel que retourné par l'API GDMS."""
    status: int                          
    apType: str
    mac: str
    name: str | None = ""
    ip: str | None = None
    upTime: int | None = None         
    usage: int
    upload: int
    download: int
    channel: int | None = None
    channel5g: int | None = None
    clients: int
    lastFwVersion: str | None = None
    versionFirmware: str | None = None
    networkId: int
    siteId: int
    ipv6: str | None = None
    longitude: str | None = None      
    latitude: str | None = None       
    remarks: str | None = None
    additionalRemarks: str | None = None


class ApListOutSchema(Schema):
    """Réponse paginée de la liste des APs."""
    result: list[ApOutSchema]
    offline: int
    total: int
    totalPage: int
    online: int
    currentPage: int