"""Modelos de presupuestos, capítulos, partidas y catálogo."""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.core.models import Organizacion
from apps.projects.models import Obra


UNIDADES = [
    ("ud", "ud"),
    ("m", "m"),
    ("m²", "m²"),
    ("m³", "m³"),
    ("kg", "kg"),
    ("h", "h"),
    ("día", "día"),
    ("pa", "PA"),
]


class PartidaCatalogo(models.Model):
    """Biblioteca personal de partidas reutilizables.

    Cada vez que se crea una partida nueva en un presupuesto, opcionalmente
    se puede guardar aquí para reutilizarla mediante autocompletado.
    """

    organizacion = models.ForeignKey(
        Organizacion, on_delete=models.CASCADE, related_name="partidas_catalogo"
    )
    descripcion = models.TextField()
    unidad = models.CharField(max_length=10, choices=UNIDADES, default="ud")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    veces_usada = models.PositiveIntegerField(default=0)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partida del catálogo"
        verbose_name_plural = "Catálogo de partidas"
        ordering = ["-veces_usada", "descripcion"]

    def __str__(self) -> str:
        return f"{self.descripcion[:60]} — {self.precio_unitario} €/{self.unidad}"


class Presupuesto(models.Model):
    ESTADO_BORRADOR = "borrador"
    ESTADO_ENVIADO = "enviado"
    ESTADO_ACEPTADO = "aceptado"
    ESTADO_RECHAZADO = "rechazado"
    ESTADO_CADUCADO = "caducado"
    ESTADOS = [
        (ESTADO_BORRADOR, "Borrador"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ACEPTADO, "Aceptado"),
        (ESTADO_RECHAZADO, "Rechazado"),
        (ESTADO_CADUCADO, "Caducado"),
    ]

    obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name="presupuestos")
    numero = models.CharField(
        max_length=20,
        blank=True,
        help_text="Se asigna automáticamente al guardar (formato AAAA-NNN).",
    )
    version = models.PositiveIntegerField(default=1)
    fecha = models.DateField(default=timezone.now)
    validez_dias = models.PositiveIntegerField(default=30)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_BORRADOR)
    iva_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        help_text="10% en reformas de vivienda que cumplen requisitos, 21% en caso general.",
    )
    notas = models.TextField(blank=True)
    enviado_en = models.DateTimeField(null=True, blank=True)
    aceptado_en = models.DateTimeField(null=True, blank=True)
    rechazado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ["-creado_en"]

    def __str__(self) -> str:
        return f"{self.numero or 'Borrador'} — {self.obra.codigo}"

    def save(self, *args, **kwargs):
        if not self.numero:
            year = self.fecha.year if self.fecha else timezone.now().year
            org = self.obra.organizacion
            ultimo = (
                Presupuesto.objects.filter(
                    obra__organizacion=org, numero__startswith=f"{year}-"
                )
                .order_by("-numero")
                .first()
            )
            siguiente = 1
            if ultimo and ultimo.numero:
                try:
                    siguiente = int(ultimo.numero.split("-")[1]) + 1
                except (IndexError, ValueError):
                    siguiente = 1
            self.numero = f"{year}-{siguiente:03d}"
        super().save(*args, **kwargs)

    @property
    def base_imponible(self) -> Decimal:
        total = Decimal("0")
        for capitulo in self.capitulos.all():
            total += capitulo.subtotal
        return total.quantize(Decimal("0.01"))

    @property
    def iva(self) -> Decimal:
        return (self.base_imponible * self.iva_porcentaje / Decimal("100")).quantize(
            Decimal("0.01")
        )

    @property
    def total(self) -> Decimal:
        return (self.base_imponible + self.iva).quantize(Decimal("0.01"))

    @property
    def editable(self) -> bool:
        return self.estado == self.ESTADO_BORRADOR


class Capitulo(models.Model):
    presupuesto = models.ForeignKey(
        Presupuesto, on_delete=models.CASCADE, related_name="capitulos"
    )
    orden = models.PositiveIntegerField(default=0)
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Capítulo"
        verbose_name_plural = "Capítulos"
        ordering = ["orden", "id"]

    def __str__(self) -> str:
        return self.nombre

    @property
    def subtotal(self) -> Decimal:
        agregado = self.partidas.aggregate(
            total=Sum(models.F("cantidad") * models.F("precio_unitario"))
        )
        return (agregado["total"] or Decimal("0")).quantize(Decimal("0.01"))


class Partida(models.Model):
    capitulo = models.ForeignKey(Capitulo, on_delete=models.CASCADE, related_name="partidas")
    orden = models.PositiveIntegerField(default=0)
    descripcion = models.TextField()
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1"))
    unidad = models.CharField(max_length=10, choices=UNIDADES, default="ud")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ["orden", "id"]

    def __str__(self) -> str:
        return f"{self.descripcion[:60]} ({self.total} €)"

    @property
    def total(self) -> Decimal:
        return (self.cantidad * self.precio_unitario).quantize(Decimal("0.01"))
