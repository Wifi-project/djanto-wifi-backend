import asyncio
from django.utils import timezone
from datetime import timedelta
from app.utils.get_api import post_data
from typing import Callable

import asyncio
import time
from datetime import datetime, timedelta, timezone


class Manager:
    def __init__(self):
        self.token: dict[str, str] = {}
        self.expire_time: dict[str, datetime] = {}
        self.thread_lock: dict[str, asyncio.Lock] = {}

    def _get_lock(self, code: str) -> asyncio.Lock:
        if code not in self.thread_lock:
            self.thread_lock[code] = asyncio.Lock()
        return self.thread_lock[code]

    async def authenticate(self, call_auth, code: str, expire_time_init: int = 20):
        lock = self._get_lock(code)

        # Lecture rapide hors verrou (optimisation)
        expire_time = self.expire_time.get(code)
        token = self.token.get(code)

        if expire_time and token and expire_time > datetime.now(timezone.utc):
            return token

        async with lock:
            # Double-check après acquisition du verrou
            expire_time = self.expire_time.get(code)
            token = self.token.get(code)

            if expire_time and token and expire_time > datetime.now(timezone.utc):
                return token

            response = await call_auth() 
            if response:
                self.token[code] = response       
                self.expire_time[code] = datetime.now(timezone.utc) + timedelta(
                    minutes=expire_time_init
                )
                return response

        return None


token_manager_instance = Manager()


async def auth(call_aut, code: str, expire_time_init: int = 20):
    return await token_manager_instance.authenticate(
        call_auth=call_aut,
        code=code,
        expire_time_init=expire_time_init,
    )