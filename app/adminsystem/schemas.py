from ninja.schema import Schema
from ninja import ModelSchema
from decimal import Decimal
from app.microtiks.models import Microtik
from app.users.models import User 
from app.users.schemas import UserResponse
from typing import List
from app.microtiks.schemas import ProfilOutSchema



class MicrotikOutListeSchemas(Schema):
    slug:str
    name: str
    owner: UserResponse



class MicrotikOutRetrieveSchemas(Schema):
    slug:str
    name: str
    description: str
    ip:str
    username: str 
    password: str
    status: str
    sold: Decimal
    users: int 
    profils: List[ProfilOutSchema]
    
    class Config:
        from_attributes = True
