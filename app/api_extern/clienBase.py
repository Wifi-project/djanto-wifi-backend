from abc import ABC, abstractmethod
from decimal import Decimal

class ClientBase(ABC):

    def __init__(self):
        self.api_key = None
        self.secret_key = None
        self.code = None


    @abstractmethod
    def urls(self) -> str:
        pass

    @abstractmethod
    async def payement(self,amount:Decimal,method:str,number:str,reference:str):
        pass