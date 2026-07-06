from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Admin panel ro'yxatida ko'rinadigan ustunlar
    list_display = ('phone', 'full_name', 'role', 'is_staff', 'is_active')
    # Filtrlash (roli va aktivligi bo'yicha)
    list_filter = ('role', 'is_staff', 'is_active')
    # Qidiruv (ism va telefon bo'yicha)
    search_fields = ('phone', 'full_name')
    # Yangi user qo'shishda ko'rinadigan maydonlar
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('full_name', 'role')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    ordering = ('phone',)


