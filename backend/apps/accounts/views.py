from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from apps.common.response import success, error
from apps.audit.services import client_ip, log_action
from .serializers import LoginSerializer, UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return error(40001, "Invalid parameters", serializer.errors)

    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if not user:
        return error(40101, "Invalid username or password", status=401)

    django_login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    log_action(
        user,
        "auth.login",
        "user",
        user.id,
        ip_address=client_ip(request),
        detail={"username": user.username},
    )

    return success({
        "token": token.key,
        "user": UserSerializer(user).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    log_action(
        request.user,
        "auth.logout",
        "user",
        request.user.id,
        ip_address=client_ip(request),
        detail={"username": request.user.username},
    )
    request.user.auth_token.delete()
    django_logout(request)
    return success(None, "Logged out")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return success(UserSerializer(request.user).data)
