from abc import ABC, abstractmethod
from typing import List

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from ninja.errors import HttpError
from ninja.security import HttpBearer
from ninja_simple_jwt.jwt.token_operations import decode_token, TokenTypes


class BasePermission(ABC):
    @abstractmethod
    def has_permission(self, request) -> bool:
        return True


class IsOwnerNetwork(BasePermission):
    def has_permission(self, request) -> bool:
        Network = apps.get_model("gdms", "Network")
        User = get_user_model()

        network_slug = request.resolver_match.kwargs.get("network_slug", "")
        user = request.user

        if not network_slug:
            raise HttpError(400, "Slug manquant")

        query = (
            Network.objects
            .prefetch_related(
                "network_owners", "gdms_network", "profils",
                "groups_vouchers", "clients"
            )
            .filter(slug=network_slug)
        )

        if getattr(request.user, "user_type", None) not in [User.ADMIN, User.OWNERSYSTEME]:
            query = query.filter(owners=user)

        network = query.first()

        if not network:
            raise HttpError(404, "Aucun network trouvé")

        request.network = network
        return True


class HasValidSubscription(BasePermission):
    def has_permission(self, request) -> bool:
        network = getattr(request, "network", None)

        if not network:
            raise HttpError(500, "Network non chargé")

        if not getattr(network, "subscription_expire_at", None):
            raise HttpError(
                status_code=403,
                message="Vous n'avez pas d'abonnement pour effectuer cette action. "
                        "Veuillez souscrire à un abonnement."
            )

        if not getattr(network, "configuration_paid", False):
            raise HttpError(
                status_code=403,
                message="Vous n'avez pas payé les frais de configuration du réseau."
            )

        if not network.subscription:
            raise HttpError(403, "Abonnement expiré ou invalide")

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
        NetworkOwner = apps.get_model("gdms", "NetworkOwner")
        Permissions = apps.get_model("permissions", "Permissions")

        user = request.user

        if not self.permissions:
            return False

        if getattr(user, "is_superuser", False):
            return True

        global_permissions = set(
            user.custom_permission_groups.values_list("permissions__code", flat=True)
        )

        network = getattr(request, "network", None)
        network_permissions = set()

        if network:
            owner_network = (
                NetworkOwner.objects
                .filter(network=network, user=user)
                .select_related("network")
                .prefetch_related("group_permissions")
                .first()
            )

            if owner_network:
                groups = owner_network.group_permissions.all()
                if groups:
                    network_permissions = set(
                        Permissions.objects
                        .filter(permissionsGroup__in=groups)
                        .values_list("code", flat=True)
                        .distinct()
                    )

        all_permissions = global_permissions | network_permissions

        if not all(perm in all_permissions for perm in self.permissions):
            raise HttpError(403, "Permission refusée")

        return True


class Auth(BasePermission):
    def has_permission(self, request) -> bool:
        return True


class PermissionsChecker(HttpBearer):
    openapi_name = "JWT"

    def __init__(
        self,
        permissions: List = None,
        owner: bool = False,
        has_subscription: bool = False,
    ):
        self.permissions = permissions if permissions is not None else []
        self.owner = owner
        self.has_subscription = has_subscription
        super().__init__()

    def authenticate(self, request, token: str):
        User = get_user_model()

        if not token:
            return None

        try:
            decoder_token = decode_token(
                token=token,
                token_type=TokenTypes.ACCESS,
                verify=True,
            )
        except Exception:
            raise HttpError(401, "Token invalide ou expiré")

        user_id = decoder_token.get("user_id")
        user = (
            User.objects
            .filter(pk=user_id)
            .prefetch_related(
                "custom_permission_groups",
                "custom_permission_groups__permissions",
            )
            .first()
)

        if not user or not user.is_active:
            raise HttpError(401, "Utilisateur introuvable ou inactif")

        request.user = user

        if self.owner:
            IsOwnerNetwork().has_permission(request)

        if self.has_subscription:
            HasValidSubscription().has_permission(request)

        if len(self.permissions) > 0:
            UserPermission(self.permissions).has_permission(request)

        return user