import jwt
from datetime import timedelta
from django.utils import timezone
from settings.settings import SECRET_KEY
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from user.models import User


def generate_jwt_token(user_id):
    expires_in = timezone.now() + timedelta(days=1)
    payload = {"user_id": user_id, "exp": expires_in}
    return jwt.encode(payload, key=SECRET_KEY, algorithm="HS256")


class add_user_authentication(BaseAuthentication):
    def authenticate(self, request):
        return request._request.user, request._request.token


class jwt_authentication(BaseAuthentication):
    keyword = "JWT"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
            try:
                user = User.objects.get(id=user_id)
                setattr(request, "user", user)
                return (user, token)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed("No such user")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired")
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed("Invalid token")


class read_only_authentication(BaseAuthentication):
    def authenticate(self, request):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return request._request.user, request._request.token
        else:
            raise exceptions.AuthenticationFailed(
                "You do not have permission to perform this action."
            )
