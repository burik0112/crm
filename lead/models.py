from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.models import User


# Create your models here.


class Client(models.Model):
    STATUS = (
        ("new", "Yangi"),
        ("first class", "Birinchi dars"),
        ("viewed", "Ko'rilgan"),
        ("coming", "Aniq keladi"),
        ("cancel", "Rad etdi"),
        ("student", "O'quvchi"),
    )

    name = models.CharField(max_length=150)  # Ism
    phone = models.CharField(max_length=20)  # Nomer

    # YANGI MAYDONLAR
    for_whom = models.CharField(max_length=100, blank=True, null=True)  # Kim uchun?
    is_from_tashkent = models.CharField(max_length=50, blank=True, null=True)  # Toshkent shaxridanmisiz?

    course = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Clients'


class ClientHistory(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    text = models.TextField()

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.client

    class Meta:
        verbose_name_plural = 'Client Histories'


class Student(models.Model):
    # Har bir o'quvchi bitta leadga bog'lanadi
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    direction = models.CharField(max_length=100)

    # TO'LOV KELISHUVI
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # Masalan: 1.000.000
    next_payment_date = models.DateField(null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)  # Qabul qilingan sana
    is_active = models.BooleanField(default=True)
    last_reminder_sent = models.DateField(
        null=True,
        blank=True,
        help_text="Oxirgi marta Telegram orqali eslatma yuborilgan sana (takror yuborilmasligi uchun)"
    )

    def is_debtor(self):
        # Agar bugungi sana keyingi to'lov sanasidan o'tib ketgan bo'lsa - qarzdor
        return date.today() > self.next_payment_date

    def __str__(self):
        return self.full_name
