from . import captcha
import Users.models as user_models
from . serializers import RegisterSerializer

from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


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
    password = request.data.get("password").strip()

    if not email or not password:
        return Response({"status": False, "message": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email.strip())

    except User.DoesNotExist:
        return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = generate_tokens(user)

    return Response(
        {
            "status": True,
            "tokens": tokens
        }, status=status.HTTP_200_OK
    )


@ratelimit(key='ip', rate='100/m', block=True)
@api_view(['POST'])
@permission_classes([AllowAny])
def Signup(request):
    name = (request.data.get('name') or '').strip().lower()
    email = (request.data.get('email') or '').strip().lower()
    gender = (request.data.get('gender') or '').strip().lower()
    password = (request.data.get('password') or '').strip().lower()
    date_of_birth = (request.data.get('date_of_birth') or '').strip().lower()

    if not all([name, email, password, gender, date_of_birth]):
        return Response(
            {
                'status': False,
                'message': 'All fields (name, email, password, date_of_birth, profile_image) are required'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if user_models.CustomUser.objects.filter(email__iexact=email).exists():
        return Response(
            {
                'status': False,
                'message': 'Email aready exists'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) not in range(8, 16):
        return Response(
            {
                'status': False,
                'message': 'Password length must be between 8 and 16'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    if gender not in ['male', 'female', 'others']:
        return Response(
            {
                'status': False,
                'message': 'Gender must be male, female or others'
            }, status=status.HTTP_400_BAD_REQUEST
        )

    user = RegisterSerializer.MeSerializer(data=request.data)
    user.is_valid(raise_exception=True)
    user.save()

    return Response(
        {
            "status": True,
            "message": "User registerd successful"
        }, status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Logout(request):
    return Response(
        {
            "status": True,
            "message": "Logout worked"
        }, status=status.HTTP_200_OK
    )