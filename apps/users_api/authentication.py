from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from users_api.models import CustomToken


class CustomTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth = request.headers.get('Authorization')

        if not auth or not auth.startswith(self.keyword):
            return None

        try:
            key = auth.split()[1]
        except IndexError:
            raise AuthenticationFailed(_('Invalid token header. No credentials provided.'))

        return self.authenticate_credentials(key)

    def authenticate_credentials(self, key):
        try:
            token = CustomToken.objects.get(key=key)
        except CustomToken.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if token.is_expired():
            token.delete()
            raise AuthenticationFailed(_('Token has expired.'))

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)
