from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router

from app.users.models import User
from app.permissions.models import Permissions, PermissionGroup
from app.permissions.schemas import (
    PermissionListSchema, 
    PermissionGroupsList, 
    PermissionGroupCreateSchema,
    AddAndRemoveInGroup,
    PermissionGroupsRetrieve
)
from app.permissions.services import (
    creat_permission_group, 
    add_permissions_on_groups,
    add_users_on_group,
    remove_permissions_on_group,
    remove_users_on_group,
    delete_group,
    retrive_group,
    update_group
)
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum


permissions = Router(tags=["Permission"])


# ------------------------------------------------------------------
# 1. LISTES ET CRÉATION (Routes statiques)
# ------------------------------------------------------------------

@permissions.get(
    "/",
    response=List[PermissionListSchema],
    summary="Afficher la liste des permissions",
    auth=([PermissionsChecker(permissions=[PermissionsEnum.PERMISSION_READ])]),
)
def permission_list(request) -> List[PermissionListSchema]:
    """afficher la liste des permissions disponibles"""
    return Permissions.objects.filter(is_active=True).order_by("-created_at")


@permissions.get(
    "/group/",
    response=List[PermissionGroupsList],
    summary="Afficher la liste des groupes de permissions",
    auth=([PermissionsChecker(permissions=[PermissionsEnum.PERMISSION_READ])]),
)
def permission_group_list(request) -> List[PermissionGroupsList]:
    """afficher la liste des groupes de permissions disponible"""
    return (
        PermissionGroup.objects.filter(is_active=True)
        .prefetch_related("users", "permissions")
        .order_by("-created_at")
    )


# PLACÉ ICI : /group/create doit être au-dessus de /group/{group_slug}
@permissions.post(
    "/group/create",
    response=PermissionGroupsList,
    summary="Création du groupe de permission",
    auth=([PermissionsChecker(PermissionsEnum.PERMISSION_CREATE)]),
)
def create_group_permissions(request, data: PermissionGroupCreateSchema):
    """la creation d'un groupe de permission a noté que le nom doit etre unique"""
    return creat_permission_group(data=data.model_dump())


# ------------------------------------------------------------------
# 2. ACTIONS SUR UN GROUPE SPÉCIFIQUE (Routes avec {group_slug})
# ------------------------------------------------------------------

@permissions.get(
    "/group/{group_slug}",
    response=PermissionGroupsRetrieve,
    summary="Afficher les detail d'un groupes de permissions",
    auth=([PermissionsChecker(permissions=[PermissionsEnum.PERMISSION_READ])]),
)
def permission_group_retrieve(
    request, group_slug: str
) -> PermissionGroupsRetrieve:
    """Afficher les detail d'un groupe de permission"""
    return retrive_group(group_slug=group_slug)


@permissions.patch(
    "/group/{group_slug}/update",
    response=PermissionGroupsList,
    summary="la modification du group de permission",
    auth=([PermissionsChecker(permissions=[PermissionsEnum.PERMISSION_UPDATE])]),
)
def update_group_permissions(
    request, group_slug: str, data: PermissionGroupCreateSchema
) -> PermissionGroupsList:
    return update_group(group_slug=group_slug, data=data.model_dump())


@permissions.post(
    "/group/{group_slug}/add-users",
    auth=([PermissionsChecker(permissions=[PermissionsEnum.PERMISSION_UPDATE])]),
    summary="Ajouter des utilisateurs dans un groupe",
)
def add_user(request, group_slug: str, data: AddAndRemoveInGroup):
    """ajouter un user a un group de permission"""
    return add_users_on_group(data=data.model_dump(), group_slug=group_slug)


@permissions.post(
    "/group/{group_slug}/add-permissions",
    auth=([PermissionsChecker(PermissionsEnum.PERMISSION_UPDATE)]),
    summary="Ajouter des permissions à un groupe",
)
def add_permissions(request, group_slug: str, data: AddAndRemoveInGroup):
    """associer une permission a un group"""
    return add_permissions_on_groups(
        data=data.model_dump(), group_slug=group_slug
    )


@permissions.delete(
    "/group/{group_slug}/remove-users",
    auth=([PermissionsChecker(PermissionsEnum.PERMISSION_UPDATE)]),
    summary="Supprimer des utilisateurs d'un groupe",
)
def remove_users_from_group(
    request, group_slug: str, data: AddAndRemoveInGroup
):
    """retirer une list ou une personne dans un group de permission"""
    return remove_users_on_group(
        group_slug=group_slug, data=data.model_dump()
    )


@permissions.delete(
    "/group/{group_slug}/remove-permissions",
    auth=([PermissionsChecker(PermissionsEnum.PERMISSION_UPDATE)]),
    summary="Supprimer des permissions d'un groupe",
)
def remove_permissions_from_group(
    request, group_slug: str, data: AddAndRemoveInGroup
):
    """retirer une liste ou une permission dans un group"""
    return remove_permissions_on_group(
        group_slug=group_slug, data=data.model_dump()
    )


@permissions.delete(
    "/group/{group_slug}/delete",
    auth=([PermissionsChecker(PermissionsEnum.PERMISSION_DELETE)]),
    summary="Supprimer le groupe de permission",
)
def delete_group_permission(request, group_slug: str):
    """supprimer le group de permission"""
    return delete_group(group_slug=group_slug)