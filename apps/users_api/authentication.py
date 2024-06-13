from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy
from users_api.models import CustomToken


class CustomTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        view = request.resolver_match.func.cls
        permission_classes = getattr(view, 'permission_classes', [])
        if 'AllowAny' in str(permission_classes):
            return None

        auth = request.headers.get('Authorization')

        if not auth or not auth.startswith(self.keyword):
            return None

        try:
            key = auth.split()[1]
        except IndexError:
            raise AuthenticationFailed(gettext_lazy('Invalid token header. No credentials provided.'))

        return self.authenticate_credentials(key)

    def authenticate_credentials(self, key):
        try:
            token = CustomToken.objects.get(key=key)
        except CustomToken.DoesNotExist:
            raise AuthenticationFailed(gettext_lazy('Invalid token.'))

        if token.is_expired():
            token.delete()
            raise AuthenticationFailed(gettext_lazy('Token has expired.'))

        if not token.user.is_active:
            raise AuthenticationFailed(gettext_lazy('User inactive or deleted.'))

        return (token.user, token)
