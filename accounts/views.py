from . import captcha
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, APIView, permission_classes


User = get_user_model()


def generate_tokens(user):
    tokens = RefreshToken.for_user(user)

    return {
        'access': str(tokens.access_token),
        'refresh': str(tokens)
    }


@api_view(['GET'])
def get_captcha(request):
    return captcha.GenerateCaptcha(request)


@api_view(['POST'])
def verify_captcha(request):
    return captcha.VerifyCaptcha(request)


@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"status": False, "message": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email.strip())

    except User.DoesNotExist:
        return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = generate_tokens(user)

    return Response({"status": True, "tokens": tokens}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Logout(request):
    return Response({"status": True, "message": "Logout worked"}, status=status.HTTP_200_OK)