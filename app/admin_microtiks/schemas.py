from enum import Enum
from decimal import Decimal
from datetime import datetime
from ninja.schema import Schema,Field


class DepositStatus(str, Enum):
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"


class MicrotikNameOut(Schema):
    name: str 



class ClientIn(Schema):
    profil_slug: str
    user_numbers : int = Field(le=200, description="maximum 200")

class ClientCreateResponse(Schema):
    username: str 
    password: str 
    

class ClientOut(Schema):
    slug: str
    phone_number:str
    code_username:str
    code_password:str
    limit_uptime:str
    profil_name:str
    microtik: MicrotikNameOut
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



class InfoDepositBase(Schema):
    phone_number: str
    amount: Decimal
    number_receve_code: str
    profil_name: str
    limit_uptime: int 


class InfoDepositOut(InfoDepositBase):
    slug: str
    status: DepositStatus
    created_at: str

    class Config:
        from_attributes = True


class InfoDepositRetrieve(InfoDepositOut):
    client: ClientOut 

