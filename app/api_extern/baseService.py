from abc import ABC, abstractmethod


class BaseService(ABC):

    def __init__(self):
        self.BASE_URL = ''
        self.code = ''
        self.secret_key = ''


    def validate(self):
        if not self.BASE_URL:
            raise ValueError("url de base est obligatoir")


    @abstractmethod
    def urls(self,):
        ...

    @abstractmethod
    async def authentication(self):
        ...


    @abstractmethod
    def signature(self):
        ...

    @abstractmethod
    def send_request(self):
        ...

    @abstractmethod
    def get_token(self):
        ...
