from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import reverse
from rest_framework.authentication import get_authorization_header
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
import jwt

User = get_user_model()
AnonymousUser.uid = "AnonymousUser"


class remove_api_prefix_middleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/api"):
            request.path_info = request.path_info[4:]


class login_check_middleware(MiddlewareMixin):

    keyword = "JWT"

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.white_list = [
            reverse("user:login"),
        ]
        self.white_list_start = []

    def process_request(self, request):

        if request.path_info in self.white_list:
            self._try_set_user_from_jwt(request, enforce=False)
            return None

        for prefix in self.white_list_start:
            if request.path_info.startswith(prefix):
                self._try_set_user_from_jwt(request, enforce=False)
                return None

        return self._try_set_user_from_jwt(request, enforce=True)

    def _try_set_user_from_jwt(self, request, enforce=False):
        auth = get_authorization_header(request).split()
        if (
            not auth
            or len(auth) < 2
            or auth[0].lower() != self.keyword.lower().encode()
        ):
            if enforce:
                return self._reject("Invalid token header. No credentials provided.")
            else:
                request.user = AnonymousUser()
                request.token = None
                return
        token = auth[1]
        try:
            payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                raise jwt.DecodeError("Missing user_id field.")
            user = User.objects.get(uid=user_id)
            request.user = user
            request.token = token
        except User.DoesNotExist:
            if enforce:
                return self._reject("No such user")
            else:
                request.user = AnonymousUser()
                request.token = None
        except jwt.ExpiredSignatureError:
            if enforce:
                return self._reject("Token expired")
            else:
                request.user = AnonymousUser()
                request.token = None
        except jwt.DecodeError as e:
            if enforce:
                return self._reject(f"Invalid token: {e}")
            else:
                request.user = AnonymousUser()
                request.token = None
        except Exception as e:
            if enforce:
                return self._reject(str(e))
            else:
                request.user = AnonymousUser()
                request.token = None

    def _reject(self, message):
        response = JsonResponse({"detail": message}, status=401)
        return response


class super_user_check_middleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.superuser_check_list_start = ["/superuser"]

    def process_request(self, request):
        for path in self.superuser_check_list_start:
            if request.path.startswith(path):
                if not request.user.is_superuser:
                    return JsonResponse({"detail": "Permission denied"}, status=403)
                return None
        return None
