"""Vistas de presupuestos.

Estrategia UX:
- Cada capítulo y partida se añade / edita / borra vía HTMX sin recargar
  la página; el servidor devuelve solo el fragmento HTML que corresponde.
- Los totales se recalculan siempre en el servidor (fuente única de verdad)
  y se re-renderizan mediante `hx-swap-oob` en el bloque de totales.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.projects.models import Obra

from .models import Capitulo, Partida, PartidaCatalogo, Presupuesto


def _get_presupuesto_editable(request, pk: int) -> Presupuesto:
    """Recupera un presupuesto de la organización del usuario si está en borrador."""
    presupuesto = get_object_or_404(
        Presupuesto.objects.select_related("obra"),
        pk=pk,
        obra__organizacion=request.user.organizacion,
    )
    if not presupuesto.editable:
        raise PermissionError("El presupuesto no está en estado borrador.")
    return presupuesto


def _parse_decimal(valor: str, por_defecto: Decimal = Decimal("0")) -> Decimal:
    if not valor:
        return por_defecto
    try:
        return Decimal(valor.replace(",", "."))
    except (InvalidOperation, AttributeError):
        return por_defecto


def _render_totales(presupuesto: Presupuesto, capitulo: Capitulo | None = None) -> str:
    """Renderiza el bloque de totales para inyectarlo con hx-swap-oob."""
    return render_to_string(
        "budgets/_totales_oob.html",
        {"presupuesto": presupuesto, "capitulo": capitulo},
    )


# ---------------------------------------------------------------------------
# Vistas principales
# ---------------------------------------------------------------------------


@login_required
def crear_presupuesto(request, obra_pk: int):
    obra = get_object_or_404(
        Obra, pk=obra_pk, organizacion=request.user.organizacion
    )
    presupuesto = Presupuesto.objects.create(obra=obra)
    return redirect("editar_presupuesto", pk=presupuesto.pk)


@login_required
def editar_presupuesto(request, pk: int):
    presupuesto = get_object_or_404(
        Presupuesto.objects.select_related("obra", "obra__cliente").prefetch_related(
            "capitulos__partidas"
        ),
        pk=pk,
        obra__organizacion=request.user.organizacion,
    )
    return render(
        request,
        "budgets/editar.html",
        {"presupuesto": presupuesto, "obra": presupuesto.obra},
    )


@login_required
def ver_presupuesto(request, pk: int):
    presupuesto = get_object_or_404(
        Presupuesto.objects.select_related("obra", "obra__cliente").prefetch_related(
            "capitulos__partidas"
        ),
        pk=pk,
        obra__organizacion=request.user.organizacion,
    )
    return render(
        request,
        "budgets/ver.html",
        {"presupuesto": presupuesto, "obra": presupuesto.obra},
    )


@login_required
@require_POST
def cambiar_estado(request, pk: int):
    presupuesto = get_object_or_404(
        Presupuesto, pk=pk, obra__organizacion=request.user.organizacion
    )
    nuevo = request.POST.get("estado", "").strip()
    validos = {
        Presupuesto.ESTADO_ENVIADO,
        Presupuesto.ESTADO_ACEPTADO,
        Presupuesto.ESTADO_RECHAZADO,
        Presupuesto.ESTADO_BORRADOR,
    }
    if nuevo not in validos:
        messages.error(request, "Estado no válido.")
        return redirect("ver_presupuesto", pk=pk)

    presupuesto.estado = nuevo
    ahora = timezone.now()
    if nuevo == Presupuesto.ESTADO_ENVIADO:
        presupuesto.enviado_en = ahora
    elif nuevo == Presupuesto.ESTADO_ACEPTADO:
        presupuesto.aceptado_en = ahora
    elif nuevo == Presupuesto.ESTADO_RECHAZADO:
        presupuesto.rechazado_en = ahora
    presupuesto.save()
    messages.success(request, f"Presupuesto marcado como {presupuesto.get_estado_display()}.")
    return redirect("ver_presupuesto", pk=pk)


# ---------------------------------------------------------------------------
# HTMX: capítulos
# ---------------------------------------------------------------------------


@login_required
@require_POST
def anadir_capitulo(request, pk: int):
    presupuesto = _get_presupuesto_editable(request, pk)
    orden_actual = presupuesto.capitulos.count()
    capitulo = Capitulo.objects.create(
        presupuesto=presupuesto,
        orden=orden_actual,
        nombre=f"Capítulo {orden_actual + 1}",
    )
    html = render_to_string(
        "budgets/_capitulo.html",
        {"capitulo": capitulo, "presupuesto": presupuesto},
        request=request,
    )
    html += _render_totales(presupuesto)
    return HttpResponse(html)


@login_required
@require_POST
def renombrar_capitulo(request, capitulo_pk: int):
    capitulo = get_object_or_404(
        Capitulo,
        pk=capitulo_pk,
        presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not capitulo.presupuesto.editable:
        return HttpResponse(status=403)
    nombre = request.POST.get("nombre", "").strip() or capitulo.nombre
    capitulo.nombre = nombre[:200]
    capitulo.save(update_fields=["nombre"])
    return HttpResponse(capitulo.nombre)


@login_required
@require_POST
def eliminar_capitulo(request, capitulo_pk: int):
    capitulo = get_object_or_404(
        Capitulo,
        pk=capitulo_pk,
        presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not capitulo.presupuesto.editable:
        return HttpResponse(status=403)
    presupuesto = capitulo.presupuesto
    capitulo.delete()
    # Devolvemos cadena vacía para que HTMX elimine el nodo, y OOB con totales.
    return HttpResponse(_render_totales(presupuesto))


# ---------------------------------------------------------------------------
# HTMX: partidas
# ---------------------------------------------------------------------------


@login_required
@require_POST
def anadir_partida(request, capitulo_pk: int):
    capitulo = get_object_or_404(
        Capitulo,
        pk=capitulo_pk,
        presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not capitulo.presupuesto.editable:
        return HttpResponse(status=403)
    orden = capitulo.partidas.count()
    partida = Partida.objects.create(capitulo=capitulo, orden=orden)
    html = render_to_string(
        "budgets/_partida_fila.html",
        {"partida": partida, "capitulo": capitulo},
        request=request,
    )
    html += _render_totales(capitulo.presupuesto, capitulo)
    return HttpResponse(html)


@login_required
@require_POST
def guardar_partida(request, partida_pk: int):
    partida = get_object_or_404(
        Partida.objects.select_related("capitulo__presupuesto"),
        pk=partida_pk,
        capitulo__presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not partida.capitulo.presupuesto.editable:
        return HttpResponse(status=403)

    descripcion = request.POST.get("descripcion", "").strip()
    cantidad = _parse_decimal(request.POST.get("cantidad", ""), Decimal("1"))
    unidad = request.POST.get("unidad", "ud").strip() or "ud"
    precio = _parse_decimal(request.POST.get("precio_unitario", ""))

    partida.descripcion = descripcion
    partida.cantidad = cantidad
    partida.unidad = unidad
    partida.precio_unitario = precio
    partida.save()

    # Autoregistro en catálogo (solo si hay descripción y precio > 0).
    if descripcion and precio > 0:
        org = partida.capitulo.presupuesto.obra.organizacion
        cat, creada = PartidaCatalogo.objects.get_or_create(
            organizacion=org,
            descripcion=descripcion,
            defaults={"unidad": unidad, "precio_unitario": precio},
        )
        if not creada:
            cat.unidad = unidad
            cat.precio_unitario = precio
            cat.veces_usada = cat.veces_usada + 1
            cat.save(update_fields=["unidad", "precio_unitario", "veces_usada", "actualizada_en"])

    html = render_to_string(
        "budgets/_partida_fila.html",
        {"partida": partida, "capitulo": partida.capitulo},
        request=request,
    )
    html += _render_totales(partida.capitulo.presupuesto, partida.capitulo)
    return HttpResponse(html)


@login_required
@require_POST
def eliminar_partida(request, partida_pk: int):
    partida = get_object_or_404(
        Partida.objects.select_related("capitulo__presupuesto"),
        pk=partida_pk,
        capitulo__presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not partida.capitulo.presupuesto.editable:
        return HttpResponse(status=403)
    capitulo = partida.capitulo
    partida.delete()
    return HttpResponse(_render_totales(capitulo.presupuesto, capitulo))


# ---------------------------------------------------------------------------
# HTMX: autocompletado desde catálogo
# ---------------------------------------------------------------------------


@login_required
def autocompletar_partida(request):
    q = request.GET.get("descripcion", "").strip()
    resultados = []
    if len(q) >= 2:
        resultados = list(
            PartidaCatalogo.objects.filter(
                organizacion=request.user.organizacion,
                descripcion__icontains=q,
            )[:8]
        )
    partida_id = request.GET.get("partida_id")
    return render(
        request,
        "budgets/_autocompletar.html",
        {"resultados": resultados, "partida_id": partida_id},
    )


@login_required
def aplicar_sugerencia(request, partida_pk: int, catalogo_pk: int):
    partida = get_object_or_404(
        Partida.objects.select_related("capitulo__presupuesto"),
        pk=partida_pk,
        capitulo__presupuesto__obra__organizacion=request.user.organizacion,
    )
    if not partida.capitulo.presupuesto.editable:
        return HttpResponse(status=403)
    sugerencia = get_object_or_404(
        PartidaCatalogo,
        pk=catalogo_pk,
        organizacion=request.user.organizacion,
    )
    partida.descripcion = sugerencia.descripcion
    partida.unidad = sugerencia.unidad
    partida.precio_unitario = sugerencia.precio_unitario
    if partida.cantidad in (None, Decimal("0")):
        partida.cantidad = Decimal("1")
    partida.save()
    html = render_to_string(
        "budgets/_partida_fila.html",
        {"partida": partida, "capitulo": partida.capitulo},
        request=request,
    )
    html += _render_totales(partida.capitulo.presupuesto, partida.capitulo)
    return HttpResponse(html)
