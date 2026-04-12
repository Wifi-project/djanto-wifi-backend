from django.core.exceptions import PermissionDenied
from app.users.models import User
from ninja.errors import HttpError
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja_simple_jwt.jwt.token_operations import decode_token, TokenTypes
from typing import TYPE_CHECKING
from app.microtiks.models import Microtik
from http import HTTPStatus
if TYPE_CHECKING:
    from app.microtiks.models import Microtik


class BasePermission:
    def has_permission(self, request):
        return True
    

class IsOwnerMicrotik(BasePermission):
    def has_permission(self, request):
        microtik_slug = request.resolver_match.kwargs.get("microtik_slug", "")
        
        if not microtik_slug:
            raise HttpError(400, "Slug manquant")

        query = (
            Microtik.objects
            .prefetch_related('profils','clients')
            .select_related("subscription")
            .filter(slug=microtik_slug)
        )

        if request.user.user_type == User.OWNERMICROTIK:
            query = query.filter(owner=request.user)

        microtik = query.first()

        if not microtik:
            raise HttpError(404, "Aucun microtik trouvé")

        request.microtik = microtik
        return True
    

class HasValidVpn(BasePermission):
    def has_permission(self, request):
        microtik = getattr(request, "microtik", None)

        if not microtik:
            raise HttpError(500, "Microtik non chargé")

        vpn = microtik.subscription

        if not (vpn and vpn.validation):
            raise HttpError(403, "Aucun abonnement VPN valide")

        request.vpn = vpn
        return True
    

class Auth(BasePermission):
    def has_permission(self, request):
        return True
    


class GlobalAuth(HttpBearer):
    openapi_name = "JWT"

    def __init__(self, permissions=None):
        self.permissions = permissions or []
        super().__init__()

    def authenticate(self, request, token):
        if not token:
            return None

        try:
            decoder_token = decode_token(
                token=token,
                token_type=TokenTypes.ACCESS,
                verify=True
            )
        except Exception:
            raise HttpError(401, "Token expiré")

        user_id = decoder_token.get('user_id')
        user = User.objects.filter(pk=user_id).first()

        if not user:
            raise HttpError(403, "Utilisateur introuvable")

        request.user = user

        for permission_class in self.permissions:
            permission = permission_class()
            if not permission.has_permission(request):
                raise HttpError(403, "Permission refusée")

        return user