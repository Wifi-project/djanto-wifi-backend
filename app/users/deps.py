from django.core.exceptions import PermissionDenied
from app.users.models import User
from ninja.errors import HttpError
from ninja.security import HttpBearer
from ninja_simple_jwt.jwt.token_operations import decode_token, TokenTypes



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
        user = User.objects.get(pk=user_id)
        request.user = user
        # if self.permissions and user.user_type not in self.permissions:
        #     raise HttpError(
        #         status_code=403,  
        #         message="Permission refusée"
        #     )
        return user



