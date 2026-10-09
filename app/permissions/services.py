from ninja.errors import HttpError
from django.http import Http404
from app.permissions.models import PermissionGroup, Permissions
from app.users.models import User
from http import HTTPStatus

def creat_permission_group(data):
    """ 
    la creation d'un group de permission
    """
    name = data.get('name', '')
    if PermissionGroup.objects.filter(name=name).exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Ce nom de groupe existe déjà."
        )
    return PermissionGroup.objects.create(**data)


def _get_group(group_slug):
    """ 
    La verification de l'existance d'un nom de group de permission
    """
    try:
        group = PermissionGroup.objects.get(slug=group_slug)
    except PermissionGroup.DoesNotExist:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun groupe associé à ce slug."
        )
    return group


def retrive_group(group_slug:str):  
    """ Recuperer les detail d'un group de permission""" 
    group = PermissionGroup.objects.filter(is_active=True, slug=group_slug).prefetch_related('users', 'permissions').first()
    if not group:
        raise HttpError(
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="Aucun group associé à ce slug."
                        )
    return group


def update_group(group_slug, data):
    group = _get_group(group_slug=group_slug)
    allowed_fields = {'name', 'description', 'is_active'} 
    filtered = {k: v for k, v in data.items() if k in allowed_fields}
    
    new_name = filtered.get('name')
    if new_name and PermissionGroup.objects.filter(name=new_name).exclude(slug=group.slug).exists():
        raise HttpError(HTTPStatus.BAD_REQUEST, "Ce nom de groupe existe déjà.")
    
    for k, v in filtered.items():
        setattr(group, k, v)
    
    group.save(update_fields=filtered.keys())
    return group

def add_permissions_on_groups(group_slug: str, data: dict[str,str]) -> dict:
    """
    Ajoute des permissions à un groupe.
    data: liste de slugs de permissions
    """
    slug = data.get("slug", [])
    group = _get_group(group_slug=group_slug)
    
    permissions = Permissions.objects.filter(slug__in=slug)
    
    count = permissions.count()
    group.permissions.add(*permissions)
    
    return {
        "status": "permissions ajouter",
        "count": count,
        "group": group.name
    }

def add_users_on_group(group_slug: str, data: dict[str,str]) -> dict:
    """
    Ajoute des utilisateurs à un groupe.
    data: liste de slugs
    """
    group = _get_group(group_slug=group_slug)
    
    slug_list = data.get("slug", [])
    users_slugs = [slug for slug in slug_list]
    users = User.objects.filter(slug__in = users_slugs)
    
    count = users.count()
    group.users.add(*users)
    
    return {
        "status": "users ajouter",
        "count": count,
        "group": group.name
    }

def remove_users_on_group(group_slug: str, data: list[str]) -> dict:
    """
    Supprime des utilisateurs d'un groupe.
    """
    group = _get_group(group_slug=group_slug)
    
    users_slug = [slug for slug in data]
    users = User.objects.filter(slug__in=data)
    
    count = users.count()
    group.users.remove(*users)
    
    return {
        "status": "users supprimer",
        "count": count,
        "group": group.name
    }

def remove_permissions_on_group(group_slug: str, data: list[str]) -> dict:
    """
    Supprime des permissions d'un groupe.
    """
    group = _get_group(group_slug=group_slug)
    
    permissions = Permissions.objects.filter(slug__in=data)
    
    count = permissions.count()
    group.permissions.remove(*permissions)
    
    return {
        "status": "permissions supprimer",
        "count": count,
        "group": group.name
    }

def delete_group(group_slug: str) -> dict:
    """
    Supprime un groupe de permissions.
    """
    group = _get_group(group_slug=group_slug)
    group.delete()
    
    return {
        "status": "group supprimer",
        "group": group.name
    }