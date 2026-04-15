import os
from app.utils.get_api import post_data

class NimbaSms:

    def __init__(self):
        self.api_key = os.getenv("NIMBA-API-KEY")
        self.code = "nimbasms"
        self.base_url = os.getenv("BASE_URL","https://api.nimbasms.com/v1")
        self.sendername = "djanto"

    def urls(self):
        url_data = {
            'send-sms': f'{self.base_url}/messages'
        }
        return url_data.get('send-sms')
    
    
    async def send(self,number:str,messsage:str):

        payload = {
            "to": [number],
            "sender_name": self.sendername,
            "message": messsage
        }

        response = await post_data(
            url=self.urls,
            payload=payload,
            token=self.api_key,
            sms=True
        )

        return {"status":"success", "message":"sms envoyer avec success."}


