from django.urls import path
from .views import (
    RequestOTPView, 
    VerifyOTPView, 
    SetPasswordView,
    LoginView,
    LogoutView,
    ForgotPasswordRequestOTPView,
    ForgotPasswordVerifyOTPView,
    ResetPasswordView,
    ProfileView,
    RegisterFirebaseTokenView,
    TestNotificationView
)


urlpatterns = [
    path('signup/request-otp/', RequestOTPView.as_view(), name='request_otp'),
    path('signup/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('signup/set-password/', SetPasswordView.as_view(), name='set_password'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/request-otp/', ForgotPasswordRequestOTPView.as_view(), name='forgot_password_request_otp'),
    path('forgot-password/verify-otp/', ForgotPasswordVerifyOTPView.as_view(), name='forgot_password_verify_otp'),
    path('forgot-password/reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Firebase token management
    path('firebase-token/', RegisterFirebaseTokenView.as_view(), name='register-firebase-token'),
    path('test-notification/', TestNotificationView.as_view(), name='test-notification'),
]