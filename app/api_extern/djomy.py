import os 
from decimal import Decimal
import hmac
import hashlib
from ninja.errors import HttpError
from app.utils.get_api import post_data
from app.api_extern.auth_manager import auth
from app.api_extern.clienBase import ClientBase


class HmacGen:
    @staticmethod
    async def hmac_generate(secret_key:str,api_key:str) -> str:

        return hmac.new(key=secret_key.encode(),msg=api_key.encode(),digestmod=hashlib.sha256).hexdigest()

    @staticmethod
    async def hmac_compare(secrete_key:str,payload:dict,signature:str) -> bool:
        new_signare = await HmacGen.hmac_generate(secret_key=secrete_key, api_key=payload)
        
        if not hmac.compare_digest(new_signare, signature):
            raise HttpError(
                status_code=404,
                message="Incorrect webhook hmac."
            )

        return True
    

class DjomyClient(ClientBase):
    
    def __init__(self):
        self.api_key = "djomy-client-1756569269779-996a" # os.getenv('DJOMY-API-KEY',"djomy-client-1756569269779-996a")
        self.secret_key = os.getenv('DJOMY-SECRET-KEY',"s3cr3t-UX7dltPbKjR6JWVuWak84jGzfhe6bOSD")
        self.base_url = os.getenv("BASE_URL","https://sandbox-api.djomy.africa/v1")
        self.code = "djomy"
        self.return_url = "https://www.test.com"


    def urls(self,key:str) -> str:
        url_data = {
            "auth":f"{self.base_url}/auth",
            "cashin":f"{self.base_url}/payments",
        }
        return url_data.get(key)
    
    
    async def payement(self,amount:Decimal,method:str,number:str,reference:str):
        data = {
                "paymentMethod": method.value,
                "payerIdentifier": number,
                "amount": int(amount),
                "countryCode": "GN",
                "description": "payement wifi avec djanto",
                "merchantPaymentReference": reference,
                "returnUrl": self.return_url,
                }
        
        hmac_signature = await HmacGen.hmac_generate(
            secret_key = self.secret_key,
            api_key = self.api_key
            )
                
        signare = f"{self.api_key}:{hmac_signature}"

        token = await auth(
            code=self.code,
            url=self.urls(key="auth"),
            api_key=signare,
            payload={},
        )
        print('********************')
        print("token",token)
        print("signature", signare)
        print('payload',data)

        response = await post_data(
            url=self.urls(key="cashin"),
            payload=data,
            token=token,
            api_key=signare
        )
        messsage = response.get("message")
        status = messsage.get('success') if messsage else False
        return {
            "status": "success" if status else "failed", 
            "message": "Retrait initier avec success" if status else f"erreur de l'initiation du retrait. {response}"
        }

