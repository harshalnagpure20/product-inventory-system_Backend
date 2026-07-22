from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Validation failed",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Registration failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Invalid credentials",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {
                    "success": True,
                    "message": "Login successful",
                    "data": serializer.validated_data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Login failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Validation failed",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "success": True,
                    "message": "Logout successful",
                },
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired refresh token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Logout failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = TokenRefreshSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "success": False,
                        "message": "Invalid refresh token",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "data": serializer.validated_data,
                },
                status=status.HTTP_200_OK,
            )
        except (TokenError, InvalidToken) as e:
            return Response(
                {
                    "success": False,
                    "message": "Token refresh failed",
                    "error": str(e),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Token refresh failed",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )