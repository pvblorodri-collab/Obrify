from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Organizacion, Usuario


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nif", "email", "creada_en")
    search_fields = ("nombre", "nif", "email")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "organizacion", "rol", "is_staff")
    list_filter = ("rol", "organizacion", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name")}),
        ("Empresa", {"fields": ("organizacion", "rol")}),
        (
            "Permisos",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "organizacion", "rol"),
            },
        ),
    )
