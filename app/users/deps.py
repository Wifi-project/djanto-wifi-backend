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


class GlobalAuth(HttpBearer):
    def __init__(self,permissions=[]):
        self.permissions = permissions
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
            raise HttpError(
                status_code=401,
                message="Votre token a expirer"
            )

        user_id = decoder_token.get('user_id')
        user = User.objects.filter(pk=user_id).first()
        request.user = user
        # if self.permissions and user.user_type not in self.permissions:
        #     raise HttpError(
        #         status_code=403,  
        #         message="Permission refusée"
        #     )
        if not user:
            raise HttpError(
                status_code= HTTPStatus.FORBIDDEN
            )
        return user


class SubscriptionVpn:
    def __call__(self, request):
        microtik = request.microtik
        
        vpn = microtik.suscription_vpn
        if not (vpn and vpn.validation):
            raise HttpError(403, "Abonnement VPN invalide ou expiré")
        
        request.vpn = vpn

        return request.user 


class MicrotikAuth:
    def __call__(self, request:HttpRequest):
        microtik_slug = request.resolver_match.kwargs.get("microtik_slug", "")
        if not microtik_slug:
            raise HttpError(400, "Le slug est obligatoire")

        user = request.user 
        
        query = (
            Microtik.objects
            .prefetch_related('profils','clients')
            .select_related("suscription_vpn")
            .filter(slug=microtik_slug)
            )
        print("******************")
        print(user)
        print(user.user_type)
        if user.user_type == User.OWNERMICROTIK:
            microtik = query.filter(owner=user)

        if not microtik:
            raise HttpError(404, "Aucun microtik trouvé")

        request.microtik = microtik.first()
        
        return user
