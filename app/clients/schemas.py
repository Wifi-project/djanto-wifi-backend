from enum import Enum
from datetime import datetime
from ninja.schema import Schema
from uuid import UUID


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class PaymentMethod(str, Enum):
    OM = "OM"  
    MOMO = "MOMO" 


class InfoDepositIn(Schema):
    payment_method: PaymentMethod
    profil_slug: str
    phone_number: str
    number_receve_code: str


class DepositResponseSchemas(Schema):
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
