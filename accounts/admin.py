from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTP
from rest_framework_simplejwt.token_blacklist import models as blacklist_models
from django.contrib.auth.models import Group


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'birth_date', 'profile_picture', 'phone_number')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)

    readonly_fields = ("date_joined", "last_login")

class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)

# Hide Blacklisted Tokens
admin.site.unregister(blacklist_models.BlacklistedToken)
admin.site.unregister(blacklist_models.OutstandingToken)

# Hide Groups from admin
admin.site.unregister(Group)

# Change admin panel branding
admin.site.site_header = "Hope Connect AI Admin"
admin.site.site_title = "Hope Connect AI Portal"
admin.site.index_title = "Welcome to Hope Connect AI Administration"