"""Custom authentication for Authorization: Bearer <token>."""

from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """Accepts 'Authorization: Bearer <token>'."""
    keyword = "Bearer"
