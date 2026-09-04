from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import SignupSerializer, UserPublicSerializer

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Accepts multipart/form-data (matches the existing frontend):
    username, email, phone, password.
    """
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors.values()))[0]
        return Response(
            {"success": False, "message": str(first_error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return Response({"success": True, "message": "Account created successfully."})


@api_view(["POST"])
@permission_classes([AllowAny])
def signin(request):
    """
    Accepts multipart/form-data or JSON: email, password.
    Returns {"user": {...}, "token": "..."} on success to match the
    frontend's `if (response.data.user)` check.
    """
    email = request.data.get("email", "")
    password = request.data.get("password", "")

    if not email or not password:
        return Response(
            {"message": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_obj = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "user": UserPublicSerializer(user).data,
            "token": token.key,
        }
    )
