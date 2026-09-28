"""Modelos de cliente y obra."""
from django.db import models

from apps.core.models import Organizacion


class Cliente(models.Model):
    organizacion = models.ForeignKey(
        Organizacion, on_delete=models.CASCADE, related_name="clientes"
    )
    nombre = models.CharField(max_length=200)
    nif = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Obra(models.Model):
    ESTADO_BORRADOR = "borrador"
    ESTADO_ACTIVA = "activa"
    ESTADO_PAUSADA = "pausada"
    ESTADO_FINALIZADA = "finalizada"
    ESTADO_CANCELADA = "cancelada"
    ESTADOS = [
        (ESTADO_BORRADOR, "Borrador"),
        (ESTADO_ACTIVA, "Activa"),
        (ESTADO_PAUSADA, "Pausada"),
        (ESTADO_FINALIZADA, "Finalizada"),
        (ESTADO_CANCELADA, "Cancelada"),
    ]

    organizacion = models.ForeignKey(
        Organizacion, on_delete=models.CASCADE, related_name="obras"
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="obras")
    codigo = models.CharField(
        max_length=50,
        help_text="Nombre corto interno, p. ej. 'Casa García'",
    )
    direccion = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_BORRADOR)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_prevista_fin = models.DateField(null=True, blank=True)
    fecha_real_fin = models.DateField(null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Obra"
        verbose_name_plural = "Obras"
        ordering = ["-creada_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["organizacion", "codigo"], name="obra_codigo_unico_por_org"
            )
        ]

    def __str__(self) -> str:
        return self.codigo
