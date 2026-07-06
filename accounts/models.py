from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Telefon raqami kiritilishi shart")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'boss')  # Superuser har doim Boss bo'ladi
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('boss', 'Direktor (Boss)'),
        ('manager', 'Lead Menejer'),
        ('accountant', 'Buxgalter'),
    )

    phone = models.CharField(max_length=20, unique=True, verbose_name="Telefon raqami")
    full_name = models.CharField(max_length=150, verbose_name="F.I.SH")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'  # Login uchun telefon ishlatiladi
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
