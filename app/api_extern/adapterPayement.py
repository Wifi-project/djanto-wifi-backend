from app.api_extern.djomy import DjomyClient
from decimal import Decimal

class AdapterPayement:
    def __init__(self, code:str):
        self.client = DjomyClient()

    async def payement(self,amount:Decimal,method:str,number:str,reference:str):
        return await self.client.payement(
            amount = amount,
            method=method,
            number=number,
            reference=reference
        )