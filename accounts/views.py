from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, OTP
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    OTPSerializer,
    PasswordResetSerializer,
    LogoutSerializer,
    FirebaseTokenSerializer,
    TestNotificationSerializer
)
from utils.response import CustomResponse
from alerts.services import FCMNotificationService
import logging

logger = logging.getLogger(__name__)


class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSerializer

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return CustomResponse.error("Email is required", status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            return CustomResponse.error("User with this email already exists", status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        otp_code = str(random.randint(1000, 9999))
        
        # Save OTP to database
        OTP.objects.create(email=email, otp=otp_code)
        
        # Send OTP via email
        try:
            send_mail(
                'Your OTP Code',
                f"Welcome to NHA Mobile Connect. To complete your registration, please use the following One-Time Password (OTP): {otp_code}.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return CustomResponse.error("Failed to send OTP", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return CustomResponse.success("OTP sent successfully")


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSerializer
    
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            # Check if OTP exists and is valid
            try:
                otp_obj = OTP.objects.get(
                    email=email, 
                    otp=otp, 
                    is_used=False,
                    created_at__gte=timezone.now() - timedelta(minutes=10)
                )
                otp_obj.is_used = True
                otp_obj.save()
                
                return CustomResponse.success("OTP verified successfully")
            except OTP.DoesNotExist:
                return CustomResponse.error("Invalid or expired OTP", status.HTTP_400_BAD_REQUEST)
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([email, password, confirm_password]):
            return CustomResponse.error("All fields are required", status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return CustomResponse.error("Passwords do not match", status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP was verified
        try:
            otp_obj = OTP.objects.filter(
                email=email, 
                is_used=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).latest('created_at')
        except OTP.DoesNotExist:
            return CustomResponse.error("Please verify OTP first", status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user_data = {
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        }
        
        serializer = UserRegistrationSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse.success("Account created successfully")
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserProfileSerializer(user).data
            }
            
            return CustomResponse.success("Login successful", data)
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return CustomResponse.success("Logout successful")
            except Exception as e:
                return CustomResponse.error("Invalid token", status.HTTP_400_BAD_REQUEST)
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return CustomResponse.success("Profile retrieved successfully", serializer.data)
    
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return CustomResponse.success("Profile updated successfully", serializer.data)
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordRequestOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSerializer
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return CustomResponse.error("Email is required", status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        if not CustomUser.objects.filter(email=email).exists():
            return CustomResponse.error("User with this email does not exist", status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        otp_code = str(random.randint(1000, 9999))
        
        # Save OTP to database
        OTP.objects.create(email=email, otp=otp_code)
        
        # Send OTP via email
        try:
            send_mail(
                'Password Reset OTP',
                f'Your password reset OTP code is: {otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return CustomResponse.error("Failed to send OTP", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return CustomResponse.success("OTP sent successfully")


class ForgotPasswordVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = OTPSerializer 
    
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            # Check if OTP exists and is valid
            try:
                otp_obj = OTP.objects.get(
                    email=email, 
                    otp=otp, 
                    is_used=False,
                    created_at__gte=timezone.now() - timedelta(minutes=10)
                )
                otp_obj.is_used = True
                otp_obj.save()
                
                return CustomResponse.success("OTP verified successfully")
            except OTP.DoesNotExist:
                return CustomResponse.error("Invalid or expired OTP", status.HTTP_400_BAD_REQUEST)
        
        return CustomResponse.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([email, password, confirm_password]):
            return CustomResponse.error("All fields are required", status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return CustomResponse.error("Passwords do not match", status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP was verified
        try:
            otp_obj = OTP.objects.filter(
                email=email, 
                is_used=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).latest('created_at')
        except OTP.DoesNotExist:
            return CustomResponse.error("Please verify OTP first", status.HTTP_400_BAD_REQUEST)
        
        # Update user password
        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            return CustomResponse.success("Password reset successfully")
        except CustomUser.DoesNotExist:
            return CustomResponse.error("User not found", status.HTTP_404_NOT_FOUND)


class RegisterFirebaseTokenView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FirebaseTokenSerializer
    
    def post(self, request):
        serializer = FirebaseTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            request.user.firebase_token = serializer.validated_data['firebase_token']
            request.user.save()
            
            return Response({
                'message': 'Firebase token registered successfully',
                'user_id': request.user.id
            })
            
        except Exception as e:
            logger.error(f"Firebase token registration failed: {str(e)}")
            return Response(
                {'error': 'Registration failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestNotificationSerializer
    
    def post(self, request):
        if not request.user.firebase_token:
            return Response(
                {'error': 'No Firebase token registered'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TestNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            success = FCMNotificationService.send_test_notification(
                request.user, 
                data.get('title', 'Test Notification'), 
                data.get('body', 'This is a test notification!')
            )
            
            if success:
                return Response({
                    'message': 'Test notification sent successfully',
                    'user_id': request.user.id
                })
            else:
                return Response(
                    {'error': 'Notification send failed'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Test notification failed: {str(e)}")
            return Response(
                {'error': 'Notification failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
