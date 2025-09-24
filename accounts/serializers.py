from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, OTP
from django.utils import timezone
from datetime import timedelta


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'confirm_password')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'full_name', 'birth_date', 'profile_picture', 'phone_number', 'email')
        read_only_fields = ('email',)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class FirebaseTokenSerializer(serializers.Serializer):
    firebase_token = serializers.CharField(min_length=50, max_length=500, required=True,
        error_messages={
            'required': 'Firebase token is required',
            'min_length': 'Invalid token format',
            'blank': 'Firebase token cannot be empty'
        }
    )


class TestNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, default='Test Notification')
    body = serializers.CharField(max_length=500, required=False, default='This is a test notification!')