from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import serializers

# Google
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Apple
import jwt
import requests


User = get_user_model()

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
        }
    }


# Request/Response serializers for docs
class SocialLoginRequestSerializer(serializers.Serializer):
    id_token = serializers.CharField(help_text="ID token received from Google/Apple SDK")

class SocialLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()


class GoogleSignupView(APIView):
    permission_classes = []  # allow any

    @extend_schema(
        request=SocialLoginRequestSerializer,
        responses={200: SocialLoginResponseSerializer},
        examples=[
            OpenApiExample(
                "Example Request",
                value={"id_token": "ya29.a0AWY7..."},
                request_only=True,
            ),
            OpenApiExample(
                "Example Response",
                value={
                    "access": "jwt_access_token_here",
                    "refresh": "jwt_refresh_token_here",
                    "user": {"id": "uuid", "email": "test@gmail.com", "full_name": "Test User"},
                },
                response_only=True,
            ),
        ],
        description="Authenticate user with Google ID token. "
                    "Flutter app obtains the ID token via Google SDK and sends it here.",
        tags=["Social-Auth"],
    )

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get("email")
            name = idinfo.get("name", "")
            google_uid = idinfo.get("sub")

            if not email:
                return Response({"error": "Google token did not return an email"}, status=status.HTTP_400_BAD_REQUEST)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": name}
            )

            return Response(generate_tokens(user), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AppleSignupView(APIView):
    permission_classes = []  # allow any

    @extend_schema(
        request=SocialLoginRequestSerializer,
        responses={200: SocialLoginResponseSerializer},
        examples=[
            OpenApiExample(
                "Example Request",
                value={"id_token": "eyJraWQiOiJ..."},
                request_only=True,
            ),
            OpenApiExample(
                "Example Response",
                value={
                    "access": "jwt_access_token_here",
                    "refresh": "jwt_refresh_token_here",
                    "user": {"id": "uuid", "email": "hidden@appleid.com"},
                },
                response_only=True,
            ),
        ],
        description="Authenticate user with Apple ID token. "
                    "Flutter app obtains the ID token via Apple SDK and sends it here.",
        tags=["Social-Auth"],
    )

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch Apple public keys
            apple_keys = requests.get("https://appleid.apple.com/auth/keys").json()["keys"]
            header = jwt.get_unverified_header(token)
            key = next(k for k in apple_keys if k["kid"] == header["kid"])
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

            decoded = jwt.decode(
                token,
                public_key,
                audience="com.your.bundle.id",  # <-- Replace with your Apple app's Bundle ID
                algorithms=["RS256"]
            )

            email = decoded.get("email")
            apple_uid = decoded.get("sub")

            if not email:
                # Apple sometimes hides email; generate placeholder
                email = f"{apple_uid}@appleid.apple.com"

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": ""}
            )

            return Response(generate_tokens(user), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
