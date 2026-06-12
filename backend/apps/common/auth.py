"""Custom authentication that supports both Bearer and Token prefixes."""

from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """Accepts both 'Authorization: Bearer <token>' and 'Authorization: Token <token>'."""
    keyword = "Bearer"
