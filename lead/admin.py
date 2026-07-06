from django.contrib import admin
from django.contrib.admin import ModelAdmin

from lead.models import Client, ClientHistory, Student


# Register your models here.


@admin.register(Client)
class ClientAdmin(ModelAdmin):

    list_display = (
        "name",
        "phone",
        "course",
        "status",
        "manager",
        "created_at",
    )


    list_filter = (
        "status",
        "course",
        "manager",
        "created_at",
    )


    search_fields = (
        "name",
        "phone",
    )


    list_per_page = 30


    fieldsets = (

        ("👤 Mijoz ma'lumotlari", {

            "fields": (

                "name",
                "phone",
                "course",

            )

        }),


        ("📞 CRM holati", {

            "fields": (

                "status",
                "manager",

            )

        }),


        ("📝 Izoh", {

            "fields": (

                "comment",

            )

        }),

    )



@admin.register(ClientHistory)
class ClientHistoryAdmin(ModelAdmin):


    list_display = (
        "client",
        "text",
        "created",
    )


    search_fields = (
        "client__name",
    )



admin.site.register(Student)