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



class InfoDepositBase(Schema):
    phone_number: str
    amount: Decimal
    number_receve_code: str
    profil_name: str
    limit_uptime: int 


class InfoDepositOut(InfoDepositBase):
    slug: str
    status: DepositStatus
    limit_uptime: str 
    created_at: datetime

    class Config:
        from_attributes = True


class InfoDepositRetrieve(InfoDepositOut):
    client: ClientOut 

