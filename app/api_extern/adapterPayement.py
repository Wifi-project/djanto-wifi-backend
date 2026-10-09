from app.api_extern.djomy import DjomyClient
from decimal import Decimal

class AdapterPayement:
    def __init__(self, code:str):
        self.client = DjomyClient()

    async def payeIn(self,amount:Decimal,method:str,number:str,reference:str,description:str):
        return await self.client.payeIn(
            amount = amount,
            method=method,
            number=number,
            reference=reference,
            description=description
        )

    async def payOut(self,message:str,amount:Decimal,beneficiary_name:str,number:str,provider:str) -> dict:
        return await self.client.payOut(
            message=message,
            amount=amount,
            beneficiary_name=beneficiary_name,
            number=number,
            provider=provider
        )