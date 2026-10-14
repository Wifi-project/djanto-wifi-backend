from enum import Enum
from datetime import datetime
from ninja.schema import Schema,Field
from uuid import UUID
from decimal import Decimal
from typing import List, Optional

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



#-------------Voucher SCHEMAS------------#
class EffectDurationMapSchema(Schema):
    d: int
    h: int
    m: int

class VoucherSchema(Schema):
    id: int
    name: str
    vocherNum: int
    usedVoucherNum: int
    effectDurationMap: EffectDurationMapSchema
    createEmail: str
    upRate: Optional[int] = None
    upRateUnit: int
    downRate: Optional[int] = None
    downRateUnit: int
    usageQuota: Optional[int] = None
    usageUnit: int
    description: Optional[str] = None
    createTimeStr: str
    expirationTimeStr: str
    availableVoucherNum: int
    usageLimitType: int
    
class VoucherGroupListResponseSchema(Schema):
    result: List[VoucherSchema]

    class Config:
        from_attributes=True


#-----la liste des vouchers dans un group 

class DetailVoucherInGourpSchema(Schema):
    id: int
    password: str
    state: int
    endUseTimeStr: str
    deviceNum: int
    usedDeviceNum: int
    effectDurationMap: EffectDurationMapSchema
    upRate: Optional[int] = None
    upRateUnit: int
    downRate: Optional[int] = None
    downRateUnit: int
    usageQuota: Optional[int] = None
    usageUnit: int
    isCanRenew: int
    remainUsageQuota: Optional[int] = None
    usageLimitType: int


class PaginatedResponseVoucherInGroupSchema(Schema):
    result: List[DetailVoucherInGourpSchema]
    total: int
    totalPage: int
    currentPage: int

    class Config:
        from_attributes=True


class VoucherIn(Schema):
    profil_slug: str
    voucher_number : int = Field(le=1000, description="maximum 1000")


class VoucherCreateResponse(Schema):
    username: str 
    password: str 
    profile_name: str
    limit_uptime: str
    

#----------------------CLIENTS SCHEMAS---------------------

class ClientItemSchema(Schema):
    id: int
    networkId: int
    clientId: str
    name: str
    ipv4: str
    ipv6: str
    channel: int
    channelClass: int
    totalBytes: int
    txBytes: int
    rxBytes: int
    rssi: int
    txRate: int
    rxRate: int
    apId: str
    ssidId: int
    ssid: str
    portalEnable: int
    assoctime: str
    dhcpManufacture: str
    dhcpOs: str
    block: int
    vlanId: str
    lastSeen: str
    firstSeen: str

class ClientPaginatedResponseSchema(Schema):
    result: List[ClientItemSchema]
    total: int
    totalPage: int
    currentPage: int

    class Config:
        from_attributes=True


#online

class SessionItemSchema(Schema):
    name: str
    clientId: str
    apName: str
    apId: str
    ssidRemark: Optional[str] = None
    ssid: str
    rssi: int
    authType: str
    policyName: str
    loginTimeStr: Optional[str] = None
    portalTimeDisplay: Optional[str] = None
    portalInfo: Optional[str] = None
    portalStats: int


class SessionPaginatedResponseSchema(Schema):
    result: List[SessionItemSchema]
    total: int
    totalPage: int
    currentPage: int
    

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
