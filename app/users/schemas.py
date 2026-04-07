from ninja import Schema, ModelSchema
from app.users.models import User


class UserResponse(Schema):
    #pour les reponses ou l'utilisateur es renvoyer.
    first_name: str
    last_name: str 
    phone_number: str 
    email: str 

    class Config:
        from_attributes = True


class UserInSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'user_type',
            'address',
        ]

class UserOutSchema(ModelSchema):
    class Meta:
        model = User
        fields = [
            'slug',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'address',
            'is_active',
            'user_type'
        ]
                

class UserUpdate(Schema):
    first_name: str | None = None
    last_name: str | None = None
    address: str | None = None
    user_type: str | None = None


class UserPasswordUpdateMe(Schema):
    password:str
    new_password:str


class UserPasswordUpdate(Schema):
    email:str
    new_password:str


class MicrotikInfo(Schema):
    slug:str
    name: str


class UserRetrieveScheama(Schema):
    slug: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    user_type: str
    address: str
    is_active: bool
    user_type: str 
    microtiks: list[MicrotikInfo]
