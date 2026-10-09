import os 
from decimal import Decimal
import hmac
import hashlib
from ninja.errors import HttpError
from app.utils.get_api import post_data
from app.api_extern.auth_manager import auth
from app.api_extern.baseService import BaseService
from django.core.mail import send_mail
from config import settings

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

class DjomyClient(BaseService):

    def __init__(self):
        self.api_key = "djomy-client-1756569269779-996a" # os.getenv('DJOMY-API-KEY',"djomy-client-1756569269779-996a")
        self.secret_key = os.getenv('DJOMY-SECRET-KEY',"s3cr3t-UX7dltPbKjR6JWVuWak84jGzfhe6bOSD")
        self.base_url = os.getenv("BASE_URL","https://sandbox-api.djomy.africa/v1")
        self.code = "djomy"
        self.return_url = "https://www.test.com"

    
    def urls(self,url:str) -> str:
        url_data = {
            "auth":f"{self.base_url}/auth",
            "cashin":f"{self.base_url}/payments",
            "cashout":f"{self.base_url}/payout-orders"
        }
        return url_data.get(url)


    async def authentication(self):
        url = self.urls(url="auth")
        x_api_key = await self.signature()

        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': x_api_key,
        }

        response = await post_data(
            url=url,
            payload={},
            headers=headers
        )
        print('la reponse postdata', response)
        if response.get('status'): 
            message = response.get('message',{})
            data = message.get('data')
            if "accessToken" in data:
                return data.get("accessToken")

        send_mail(
            subject="Erreur d'authentification djomy",
            message=f"une erreur d'authentification s'est produit {response}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,  
        )
        return None


    async def get_token(self):
        token = await auth(
            call_aut=self.authentication,
            code=self.code,
            expire_time_init=3000
        )
        return token

    async def signature(self):
        hmac_signature = await HmacGen.hmac_generate(
            secret_key = self.secret_key,
            api_key = self.api_key
            )
                
        return f"{self.api_key}:{hmac_signature}"


    async def send_request(self,url:str, payload:dict |None = None):
        signature = await self.signature()
        token = await self.get_token()

        if not token:
            raise HttpError(
                status_code=401,
                message="erreur d'authentification pas de token provider"
            )

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {token}",
            'X-API-KEY': signature
        }

        response = await post_data(url=url,payload=payload,headers=headers)
        if response.get('status'):
            messsage = response.get('message')
            data = messsage.get('data')
            if data:
                return data
            
        send_mail(
            subject="Erreur de payement",
            message=f"une erreur s'est produit pendant le paiement {response}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,  
        )
        return None


    async def payeIn(self,amount:Decimal,method:str,number:str,reference:str, description:str):
        url = self.urls(url='cashin')

        payload = {
                "paymentMethod": method,
                "payerIdentifier": number,
                "amount": int(amount),
                "countryCode": "GN",
                "description": description,
                "merchantPaymentReference": reference,
                "returnUrl": self.return_url,
            }

        return await self.send_request(url=url,payload=payload)
        


    async def payOut(self,message:str,amount:Decimal,beneficiary_name:str,number:str,provider:str):
        url = self.urls(url='cashout')

        items = {
            "message": message,
            "amount": amount,
            "beneficiary":{
                "name": beneficiary_name
            },
            "destination": {
                "type": "WALLET",
                "countryCode": "GN",
                "currencyCode": "GNF",
                "account": {
                    "accountNumber":number,
                    "providerCode": provider
                }
            }
        }

        payload = {
            'description': message,
            'items': [items]
        }

        return self.send_request(url=url,payload=payload)


    async def webhook(self):
        ...