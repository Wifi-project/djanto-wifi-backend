from ninja import Schema
from typing import Optional
from datetime import datetime,date
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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True

    # @staticmethod
    # def resolve_network_slug(obj):
    #     return obj.network.slug if obj.network else None

    # @staticmethod
    # def resolve_profil_name(obj):
    #     return obj.profil.name if obj.profil else None

    # @staticmethod
    # def resolve_category_name(obj):
    #     return obj.category.name if obj.category else None



#____________ voucher paiement ______________

class ClientLogTransactions(Schema):
    phone_number: str | None = None
    code_username: str | None = None
    profil_name: str | None = None
    amount: Decimal = Decimal("0")
    sms_send: bool = False

    class Config:
        from_attributes = True


class TransactionOutIntransaction(Schema):
    slug: str
    transaction_id: Optional[str] = None
    phone_number: Optional[str] = None
    amount: Decimal
    payment_method: str
    type: str
    status: str
    client_transactions: ClientLogTransactions | None = None
    created_at: date

    class Config:
        from_attributes = True


class TransactionVoucherListOut(Schema):
    result: list[TransactionOutIntransaction]
    total: int
    totalPage: int
    currentPage: int


class TransactionListOut(Schema):
    result: list[TransactionOut]
    total: int
    totalPage: int
    currentPage: int



#-------------- Webhook -----------------

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

# --- 1. Données internes pour les paiements ---
class PaymentData(BaseModel):
    transactionId: str
    status: str
    paidAmount: int
    receivedAmount: int
    fees: int
    paymentMethod: str
    merchantPaymentReference: str
    payerIdentifier: str
    currency: str
    createdAt: datetime

# --- 2. Données internes pour les transferts (Payouts) ---
class PayoutData(BaseModel):
    payoutId: str
    reference: str
    orderReference: Optional[str] = None
    status: str
    amount: int
    fees: int
    currency: str
    provider: str
    destinationAccountNumber: str
    beneficiaryName: str
    providerReference: Optional[str] = None
    createdAt: datetime

# --- 3. Conteneur "data" flexible (V2) ---
# En V2, soit "payment" est présent, soit "payout" est présent (jamais les deux en même temps)
class WebhookDataContainer(BaseModel):
    payment: Optional[PaymentData] = None
    payout: Optional[PayoutData] = None

# --- 4. Le Payload Global du Webhook ---
class WebhookPayload(BaseModel):
    message: str
    eventType: str
    eventId: str
    data: WebhookDataContainer
    paymentLinkReference: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None



class ResponseSchemas(BaseModel):
    status: str
    message: str