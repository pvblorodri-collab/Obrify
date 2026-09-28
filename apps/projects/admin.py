from django.contrib import admin

from .models import Cliente, Obra


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nif", "email", "telefono", "organizacion")
    list_filter = ("organizacion",)
    search_fields = ("nombre", "nif", "email")


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ("codigo", "cliente", "estado", "fecha_inicio", "fecha_prevista_fin")
    list_filter = ("estado", "organizacion")
    search_fields = ("codigo", "direccion", "cliente__nombre")
    date_hierarchy = "creada_en"
