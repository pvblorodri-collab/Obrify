from django.contrib import admin

from .models import Capitulo, Partida, PartidaCatalogo, Presupuesto


class PartidaInline(admin.TabularInline):
    model = Partida
    extra = 0


class CapituloInline(admin.TabularInline):
    model = Capitulo
    extra = 0


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ("numero", "obra", "fecha", "estado", "total")
    list_filter = ("estado",)
    search_fields = ("numero", "obra__codigo", "obra__cliente__nombre")
    date_hierarchy = "fecha"
    inlines = [CapituloInline]


@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ("nombre", "presupuesto", "orden", "subtotal")
    list_filter = ("presupuesto__obra__organizacion",)
    inlines = [PartidaInline]


@admin.register(PartidaCatalogo)
class PartidaCatalogoAdmin(admin.ModelAdmin):
    list_display = ("descripcion_corta", "unidad", "precio_unitario", "veces_usada")
    search_fields = ("descripcion",)
    list_filter = ("organizacion",)

    @admin.display(description="Descripción")
    def descripcion_corta(self, obj):
        return obj.descripcion[:80]
