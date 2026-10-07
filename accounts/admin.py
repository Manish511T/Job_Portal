from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields':('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra info', {'fields': ('email', 'role')}),
    )