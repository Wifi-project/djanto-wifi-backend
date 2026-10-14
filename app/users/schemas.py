from ninja import Schema, ModelSchema
from app.users.models import User
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from pydantic import Field, EmailStr
from datetime import date

class UserResponse(Schema):
    #pour les reponses ou l'utilisateur es renvoyer.
    first_name: str
    last_name: str 
    phone_number: str 
    email: str 

    class Config:
        from_attributes = True


class UserInSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'user_type',
            'address',
        ]

class UserOutSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            'slug',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'address',
            'is_active',
            'user_type'
        ]


class NetworkBasicSchema(Schema):
    slug: str
    name: str
    description: str | None
    network_id: int | str | None = None
    wallet_balance: Decimal
    subscription_expire_at: date | None = None
    admin_blocked: bool
    commission_rate: Decimal
    subscription_at: date | None = None
    configuration_paid: bool
    subscription: int
    days_remaining: int


class PermissionSchema(Schema):
    slug: str
    name: str
    # code: str

class PermissionGroupSchemas(Schema):
    name: str


class PermissionGroupInCurrentSchemas(Schema):
    #utiliser dans current user
    name: str
    permissions: list[PermissionSchema]


class NetworkkOwnerSchema(Schema):
    slug: str
    network: NetworkBasicSchema
    group_permissions: List[PermissionGroupSchemas]
    status: str
    created_at: datetime

class CurrentUserSchema(Schema):
    slug: str
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    user_type: str
    address: Optional[str] = None
    is_active: bool
    network_owner_trough: List[NetworkkOwnerSchema]
    custom_permission_groups: list[PermissionGroupInCurrentSchemas]


class UserUpdate(Schema):
    first_name: str | None = None
    last_name: str | None = None
    address: str | None = None
    # user_type: str | None = None


class UserPasswordUpdateMe(Schema):
    password:str
    new_password:str


class UserPasswordUpdate(Schema):
    email:str
    new_password:str


class NetworkInfo(Schema):
    slug:str
    name: str
    description: str


class UserRetrieveScheama(Schema):
    slug: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    user_type: str
    address: str
    is_active: bool
    user_type: str 
    owners_network : list[NetworkInfo]


class UserOwnerOutSchema(Schema):
    slug: str
    first_name: str
    last_name: str
    email: str
    phone_number: str


# class CreateOwnerSchemas(Schema):
#     first_name: str
#     last_name: str
#     email: str
#     phone_number: str

class CreateOwnerSchemas(Schema):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=1)
    email: EmailStr 

class AddOwnerSchemas(Schema):
    email:str