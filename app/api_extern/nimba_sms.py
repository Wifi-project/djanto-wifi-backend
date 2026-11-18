import os
import base64
from app.utils.get_api import post_data
from app.commone.email import sender_email
from config.settings import ADMIN_EMAIL

class NimbaSms:

    def __init__(self):
        
        self.code = "nimbasms"
        self.base_url = os.getenv("BASE_URL_NIMBA","https://api.nimbasms.com/v1/")
        self.sendername = os.getenv("SENDER_NAME","Djantowifi")
        self.authorization = os.getenv("AUTHORIZATION_NIMBA","UXHMqdkVpOpYV8RJmwzedxnv2pwRjZ_Z5uef4xrP-4XwchPDwC5EYnm_YAJJXKKQ0_e5iUXCyrhqtGnS2I2KziWB7jVPn_VEw5c-H5n_UII") 

    async def urls(self, value):
        url_data = {
            'send-sms': f'{self.base_url}messages'
        }
        return url_data.get(value)
    
    async def send(self, number: str, message: str):
        url = await self.urls(value='send-sms')

        payload = {
            "to": [number],
            "sender_name": self.sendername,
            "message": message
        }

        headers = {
            "Authorization": f"{self.authorization}",
            "content-type": "application/json"
        }

        response = await post_data(
            url= url,
            payload=payload,
            headers=headers
        )
        if response.get('status'):
            msg = response.get("message")
            if msg and msg.get("messageid"):
                return {"status": "success", "message": "sms envoyé avec succès."}

        sender_email(
            subject="Erreur SMS",
            message=f"une erreur lors de l'envoie de sms {response}",
            recipient_list=[ADMIN_EMAIL]
        )
        return {"status": "failled", "message": "erreur lors de l'envoie du sms."}


send_sms = NimbaSms()