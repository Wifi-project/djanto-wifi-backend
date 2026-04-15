import asyncio
from django.utils import timezone
from datetime import timedelta
from app.utils.get_api import post_data

class Manager:
    
    def __init__(self):
        self.token = {}
        self.expire_time = {}
        self.thread_lock = {}

    
    async def authenticate(
            self,
            code:str,
            url:str,
            expire_time_init: int,
            api_key:str | None = None, 
            payload:dict | None = None,
                ):
        
        if code not in self.thread_lock:
            self.thread_lock[code] = asyncio.Lock()

        expire = self.expire_time.get(code)
        token = self.token.get(code)

        if token and expire > timezone.now():
            return token
        
        async with self.thread_lock[code]:

            if token and expire > timezone.now():
                return token
            
            response = await post_data(
                url=url,
                payload=payload,
                api_key=api_key if api_key else None
            )

            message = response.get('message')
            if message and message.get('data'):
                new_token = message['data'].get('accessToken')
            else:
                new_token = response.get('access') or response.get('token')

            self.token[code] = new_token
            self.expire_time_init = timezone.now() + timedelta(minutes=expire_time_init)
            
            return new_token


token_manager_instance = Manager()


async def auth(code:str,url:str,api_key:str = None,payload:dict = None,expire_time_init: int =20):
    return await token_manager_instance.authenticate(
        code=code,
        url=url,
        api_key=api_key,
        payload=payload,
        expire_time_init=expire_time_init
    )