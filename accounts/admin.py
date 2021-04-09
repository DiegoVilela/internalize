from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_select_related = ('client',)
    list_display = (
        'username',
        'email',
        'client',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'last_login',
        'is_approved',
    )
    list_filter = (
        'last_login',
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'client',
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Client'), {'fields': ('client',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
