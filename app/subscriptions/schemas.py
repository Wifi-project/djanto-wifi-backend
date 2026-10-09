from ninja import ModelSchema, Field
from typing import Optional
from ninja.schema import Schema
from decimal import Decimal
from enum import Enum
from datetime import datetime, date
from pydantic import IPvAnyAddress
from app.clients.schemas import PaymentMethod
from pydantic import field_validator


class SubscriptionCategoriEnum(str, Enum):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"

#----------------- Prix de base au WG -----------------------#

class PriceBaseOut(Schema):
    slug: str
    price: Decimal

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

class PriceBaseUpdate(Schema):
    price: Decimal | None = None
    is_active: bool | None = None
        

class PriceBaseInt(Schema):
    price: Decimal | None = None
    

#------------------Subscription Categorie abonement WG ---------------#


class SubscriptionCategorieIntSchema(Schema):
    name: str = Field(..., max_length=100)
    days: int | None = Field(default=0)
    months: int | None = Field(default=0)
    discount: Decimal

    @field_validator('days')
    def validate_days(cls, v):
        if v is not None and v < 0:
            raise ValueError('Les jours ne peuvent pas être négatifs')
        if v is not None and v > 365:
            raise ValueError('Les jours ne peuvent pas dépasser 365')
        return v

    @field_validator('months')
    def validate_months(cls, v):
        if v is not None and v < 0:
            raise ValueError('Les mois ne peuvent pas être négatifs')
        if v is not None and v > 12:
            raise ValueError('Les mois ne peuvent pas dépasser 60')
        return v

class SubscriptionCategorieUpdateSchema(SubscriptionCategorieIntSchema):
    is_active: bool


class SubscriptionCategorieOutShema(Schema):
    slug: str 
    name: str
    days: int
    discount: Decimal
    price: Decimal | None = None

    class Config:
        from_attributes = True


#------------- Paiement Subscription --------------#
class PaidSubscriptionBaseSchema(Schema):
    """Schéma de base pour un paiement"""
    slug: str 
    phone_number: str
    duration_days: int 
    amount: Decimal
    action: str 
    status: str 
    created_at: datetime 
    updated_at: datetime 


class PaidSubscriptionListSchema(PaidSubscriptionBaseSchema):
    """Schéma pour la liste des paiements"""
    category_name: str 
    category_slug: str 
    
    class Config:
        from_attributes = True


class PaidSubscriptionDetailSchema(PaidSubscriptionBaseSchema):
    """Schéma pour le détail d'un paiement"""
    category: 'SubscriptionCategorieOutShema'
    subscription: Optional['SubscriptionWGListSchema'] 
    
    class Config:
        from_attributes = True


# ------------------ Schémas pour SubscriptionWG --------------------#

class AddInformationMicrotik(Schema):
    """Ajout des informations de connextion au microtik"""
    username_routeur: str 
    password_routeur: str 

class SubscriptionWGBaseSchema(Schema):
    """Schéma de base pour un abonnement"""
    slug: str 
    mac_address: str | None = None
    serial_number: str | None = None
    gdms_network_id: int | None = None 
    gdms_site_id: int | None = None

    wg_client_id: str | None = None
    wg_ip: IPvAnyAddress | None = None
    wg_public_key: str | None = None
    mikrotik_username: str 
    expire_at: datetime | None = None
    is_active: bool 
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SubscriptionWGupdateSchema(Schema):
    """Mise a jour des access """
    mac_address: str | None = None
    serial_number: str | None = None
    gdms_network_id: int | None = None 
    gdms_site_id: int | None = None



class SubscriptionWGListSchema(SubscriptionWGBaseSchema):
    """Schéma pour la liste des abonnements afficher dans les details de la transaction"""
    microtik_name: str
    microtik_slug: str 
    microtik_owner: str
    validation: bool
    days_remaining: int
    
    class Config:
        from_attributes = True


class SubscriptionWGDetailSchema(SubscriptionWGBaseSchema):
    """Schéma pour le détail d'un abonnement afficher dans les details du microtik"""
    validation: bool 
    days_remaining: int 
    category_name: str | None = None
    category_slug:  str | None = None
    
    class Config:
        from_attributes = True



# ------------------ Schémas de sortie pour les endpoints --------------------#

class SubscriptionWGOutSchema(Schema):
    """Schéma de sortie pour la création d'abonnement"""
    success: bool = Field(..., description="Succès ou échec")
    message: str = Field(..., description="Message")
    subscription: Optional[SubscriptionWGDetailSchema] = Field(None, description="Détails de l'abonnement")
    payment: Optional[PaidSubscriptionBaseSchema] = Field(None, description="Détails du paiement")


class SubscriptionListResponse(Schema):
    """Réponse pour la liste des abonnements"""
    count: int = Field(..., description="Nombre total d'abonnements")
    results: list[SubscriptionWGListSchema] = Field(..., description="Liste des abonnements")


class PaidSubscriptionListResponse(Schema):
    """Réponse pour la liste des paiements"""
    count: int = Field(..., description="Nombre total de paiements")
    results: list[PaidSubscriptionListSchema] = Field(..., description="Liste des paiements")



#----------------- Subscription WG ------------------#

class SubscribsionEnum(str,Enum):
    CURRENT = "current"
    SUBSCRIPTION = "subscription "
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    SUBSCRIPTION_USED = "subscription_used"

class SubscriptionWgInSchema(Schema):
    paymentMethod: PaymentMethod
    phone_number: str 
    category_slug: str


class ConfigurationInSchema(Schema):
    paymentMethod: PaymentMethod
    phone_number: str 

class SubscriptionResponse(Schema):
    status: str 
    message: str 


class SubscriptionWgOutSchema(Schema):
    slug: str
    wg_client_id: Optional[str] = None
    wg_ip: Optional[IPvAnyAddress] = None
    wg_public_key: Optional[str] = None  
    mikrotik_username: str
    expire_at: Optional[date] = None 
    is_paid: Optional[bool] = None 
    validation: Optional[bool] = None 
    days_remaining: Optional[int] = None    
    # category: Optional[SubscriptionCategorieOutShema] = None 
    
    @field_validator('validation', mode='before')
    def validate_validation(cls, v, info):
        ...
        
    class Config:
        from_attributes = True


class SubscriptionWgRetrieveOutSchema(Schema):
    slug: str
    wg_client_id: Optional[str] = None
    wg_ip: Optional[IPvAnyAddress] = None
    wg_public_key: Optional[str] = None  
    mikrotik_username: str
    expire_at: Optional[date] = None 
    is_paid: Optional[bool] = None 
    validation: Optional[bool] = None 
    days_remaining: Optional[int] = None 
    status: SubscribsionEnum
    category: Optional[SubscriptionCategorieOutShema] = None 
    # suscription_wg: 




#---------------------webhook---------------------------------
class WebHookData(Schema):
    transactionId: str
    status: str 
    paidAmount: int 
    receivedAmount: int
    fees: int 
    paymentMethod: str
    merchantPaymentReference: str 
    payerIdentifier: str 
    currency: str
    createdAt: str


class WebhookSchema(Schema):
    message: str
    eventType: str
    eventId: str
    data: WebHookData
    paymentLinkReference: str
    timestamp: str

class WebhookOutSchemas(Schema):
    status: str
    message: str