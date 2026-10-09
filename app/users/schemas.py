from ninja import Schema, ModelSchema
from app.users.models import User
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from pydantic import Field, EmailStr

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


class MicrotikBasicSchema(Schema):
    slug: str
    name: str
    description: str | None
    wallet_balance: Decimal
    users_count: int
    is_online: bool
    admin_blocked: bool
    commission_rate: Decimal
    amount_available_windrawal: Decimal

class PermissionSchema(Schema):
    slug: str
    name: str
    code: str

class MicrotikOwnerSchema(Schema):
    slug: str
    microtik: MicrotikBasicSchema
    permissions: List[PermissionSchema]  
    is_active: bool
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
    microtik_owner_trough: List[MicrotikOwnerSchema]

                

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


class MicrotikInfo(Schema):
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
    owners_microtik : list[MicrotikInfo]


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