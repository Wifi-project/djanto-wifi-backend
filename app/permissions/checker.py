from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from django.core.exceptions import ObjectDoesNotExist
from ninja.errors import HttpError
from ninja.security import HttpBearer
from ninja_simple_jwt.jwt.token_operations import decode_token, TokenTypes

from app.users.models import User
from app.microtiks.models import Microtik

if TYPE_CHECKING:
    from app.microtiks.models import Microtik


class BasePermission(ABC):
    @abstractmethod
    def has_permission(self, request) -> bool:
        return True


class IsOwnerMicrotik(BasePermission):
    def has_permission(self, request) -> bool:
        microtik_slug = request.resolver_match.kwargs.get("microtik_slug", "")
        user = request.user 

        if not microtik_slug:
            raise HttpError(400, "Slug manquant")

        query = (
            Microtik.objects
            .prefetch_related("profils", "clients","owners","microtik_owners")
            .select_related("subscriptionwg")
            .filter(slug=microtik_slug)
        )

        if getattr(request.user, "user_type", None) not in [User.ADMIN, User.OWNERSYSTEME]:
            query = query.filter(owners= user)


        microtik = query.first()

        if not microtik:
            raise HttpError(404, "Aucun microtik trouvé")

        # microtik_owner = microtik.owners.filter(user=user).first()
        # permissions = set(perm for perm in microtik_owner.permissions.all())

        # if not all()

        request.microtik = microtik
        return True


class HasValidWG(BasePermission):
    def has_permission(self, request) -> bool:
        microtik = getattr(request, "microtik", None)

        if not microtik:
            raise HttpError(500, "Microtik non chargé")

        try:
            wg = getattr(microtik, "subscriptionwg", None)
        except ObjectDoesNotExist:
            wg = None

        if not wg:
            raise HttpError(403, "Aucun abonnement VPN trouvé")

        if not getattr(wg, "validation", False):
            raise HttpError(403, "Abonnement VPN expiré ou invalide")

        request.subscription = wg
        return True


class UserPermission(BasePermission):
    def __init__(self, permissions: List[str] = None):
        if permissions is None:
            permissions = []
        self.permissions = [
            perm.value if hasattr(perm, "value") else perm
            for perm in permissions
        ]

    def has_permission(self, request) -> bool:
        user = request.user

        if not self.permissions:
            return False

        if getattr(user, "is_superuser", False):
            return True

        global_permissions = set(
            user.custom_permission_groups.values_list("permissions__code", flat=True)
        )

        microtik = getattr(request, "microtik", None)
        microtik_permissions = set()

        if microtik:
            microtik_owner = getattr(user, 'microtik_owner_trough', None)
            if microtik_owner:
                microtik_owner_instance = microtik_owner.filter(microtik=microtik).first()
                if not microtik_owner_instance and microtik_owner_instance.is_active is None:
                    raise HttpError(403, "Vous avez été bloquer de ce routeur.")
                
                microtik_permissions = set(
                    microtik_owner_instance.permissions.values_list('code', flat=True)
                )

        all_permissions = global_permissions | microtik_permissions

        if not all(perm in all_permissions for perm in self.permissions):
            raise HttpError(403, "Permission refusée")

        return True



class Auth(BasePermission):
    def has_permission(self, request) -> bool:
        return True


class PermissionsChecker(HttpBearer):
    openapi_name = "JWT"

    def __init__(self, permissions: List = None, owner: bool = False, hasWG: bool = False):
        self.permissions = permissions if permissions is not None else []
        self.owner = owner
        self.hasWG = hasWG
        super().__init__()

    def authenticate(self, request, token: str):
        if not token:
            return None

        try:
            decoder_token = decode_token(
                token=token,
                token_type=TokenTypes.ACCESS,
                verify=True
            )
        except Exception:
            raise HttpError(401, "Token invalide ou expiré")

        user_id = decoder_token.get("user_id")
        user = (
            User.objects.filter(pk=user_id)
            .prefetch_related("owners_microtik","microtik_owner_trough")
            .first()
            )

        if not user or not user.is_active:
            raise HttpError(401, "Utilisateur introuvable ou inactif")

        request.user = user

        if self.owner:
            IsOwnerMicrotik().has_permission(request)

        if self.hasWG:
            HasValidWG().has_permission(request)

        if len(self.permissions) > 0:
            UserPermission(self.permissions).has_permission(request)

        return user