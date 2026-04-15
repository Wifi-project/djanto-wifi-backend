from enum import Enum
from datetime import datetime
from ninja.schema import Schema,Field
from uuid import UUID
from decimal import Decimal

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class PaymentMethod(str, Enum):
    OM = "OM"  
    MOMO = "MOMO" 
    PAYCARD = "PAYCARD"
    SOUTRA_MONEY = "SOUTRA_MONEY"



class InfoDepositIn(Schema):
    paymentMethod: PaymentMethod
    profil_slug: str
    phone_number: str
    number_receve_code: str


class DepositResponseSchemas(Schema):
    status: str 
    message: str 


class PaymentResponseSchema(Schema):
    status: str
    slug: str
    amount: Decimal
    paymentMethod: str 


# --- Exemple d'ut

#-------------CLIENT SCHEMAS------------#

class MicrotikNameOut(Schema):
    name: str 



class ClientIn(Schema):
    profil_slug: str
    user_numbers : int = Field(le=1000, description="maximum 1000")


class ClientCreateResponse(Schema):
    username: str 
    password: str 
    profile_name: str
    limit_uptime: str
    

class ClientOut(Schema):
    slug: str
    phone_number:str | None = None
    code_username:str
    code_password:str
    limit_uptime:str | None = None
    profil_name:str
    microtik_name: str = Field(None, alias="microtik.name")
    generate: str 
    is_sold: bool
    status: str
    created_at: datetime | None = None


    class Config:
        from_attributes=True


class ClientRetrieve(ClientOut):
    microtik: MicrotikNameOut


class ClientActifSchema(Schema):
    username: str
    ip: str
    connexion_time: str  
    expire_in: int


class ClientNoExpireSchema(Schema):
    name: str
    limit_uptime: str
    uptime: str 
    address: str
    profile: str
    disabled: str


class ClientBlockedOutSchemas(Schema):
    status: str 
    message: str 





#------------WEB HOOK----------------

class PaymentData(Schema):
    transaction_id: UUID 
    status: str
    paid_amount: float 
    received_amount: float 
    fees: float
    payment_method: str
    merchant_payment_reference: str 
    payer_identifier: str 
    currency: str = "GNF"
    created_at: datetime 


class PaymentWebhook(Schema):
    message: str
    event_type: str 
    event_id: UUID 
    data: PaymentData
    payment_link_reference: str
    timestamp: datetime

    class Config:
        # Permet d'utiliser les noms Python (snake_case) 
        # tout en acceptant le JSON en camelCase
        populate_by_name = True
