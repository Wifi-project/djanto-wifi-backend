from ninja.schema import Schema, Field
from ninja import ModelSchema
from typing import List
from app.users.schemas import UserResponse

class PermissionListSchema(Schema):
    slug: str
    name: str | None
    code: str | None
    description: str = ""

    class Config:
        from_attributes = True


class PermissionGroupsList(Schema):
    slug: str
    name: str | None
    description: str | None
    is_active: bool


class PermissionGroupsRetrieve(Schema):
    slug: str
    name: str | None
    description: str | None
    is_active: bool
    users: List[UserResponse] = []
    permissions: List[PermissionListSchema] = []


class PermissionGroupCreateSchema(Schema):
    name :str 
    description: str  


class AddAndRemoveInGroup(Schema):
    slug : list[str]

