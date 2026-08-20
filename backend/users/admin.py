from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class OndaUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (
            "Onda",
            {
                "fields": (
                    "display_name",
                    "email_verified_at",
                    "recovery_username",
                    "bio",
                    "avatar",
                    "home_city",
                    "is_private",
                    "status",
                    "deletion_due_at",
                    "created_at",
                )
            },
        ),
    )
    readonly_fields = UserAdmin.readonly_fields + ("created_at",)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Onda",
            {
                "fields": (
                    "email",
                    "display_name",
                    "is_private",
                )
            },
        ),
    )
