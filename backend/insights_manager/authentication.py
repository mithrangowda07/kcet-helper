from rest_framework import authentication, exceptions
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from insights_manager.models import AdminAccount


class AdminJWTAuthentication(authentication.BaseAuthentication):
    """Authenticate platform admins via Bearer JWT with token_type=admin."""

    keyword = 'Bearer'

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].decode().lower() != self.keyword.lower():
            return None

        if len(header) == 1:
            raise exceptions.AuthenticationFailed('Invalid Authorization header.')
        if len(header) > 2:
            raise exceptions.AuthenticationFailed('Invalid Authorization header.')

        raw_token = header[1].decode()
        admin = self._get_admin_from_token(raw_token)
        return (admin, raw_token)

    def _get_admin_from_token(self, raw_token: str) -> AdminAccount:
        try:
            token_backend = TokenBackend(
                algorithm='HS256',
                signing_key=self._get_signing_key(),
            )
            validated = token_backend.decode(raw_token, verify=True)
        except (InvalidToken, TokenError) as exc:
            raise exceptions.AuthenticationFailed('Invalid or expired admin token.') from exc

        if validated.get('token_type') != 'admin':
            raise exceptions.AuthenticationFailed('Invalid admin token type.')

        admin_id = validated.get('admin_id')
        if not admin_id:
            raise exceptions.AuthenticationFailed('Invalid admin token payload.')

        try:
            admin = AdminAccount.objects.get(pk=admin_id, is_active=True)
        except AdminAccount.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('Admin account not found or inactive.') from exc

        return admin

    def _get_signing_key(self):
        from django.conf import settings

        return settings.SECRET_KEY
