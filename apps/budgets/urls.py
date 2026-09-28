from django.urls import path

from . import views

urlpatterns = [
    # Vistas principales
    path("obra/<int:obra_pk>/crear/", views.crear_presupuesto, name="crear_presupuesto"),
    path("<int:pk>/editar/", views.editar_presupuesto, name="editar_presupuesto"),
    path("<int:pk>/ver/", views.ver_presupuesto, name="ver_presupuesto"),
    path("<int:pk>/estado/", views.cambiar_estado, name="cambiar_estado_presupuesto"),

    # HTMX capítulos
    path("<int:pk>/capitulos/anadir/", views.anadir_capitulo, name="anadir_capitulo"),
    path(
        "capitulos/<int:capitulo_pk>/renombrar/",
        views.renombrar_capitulo,
        name="renombrar_capitulo",
    ),
    path(
        "capitulos/<int:capitulo_pk>/eliminar/",
        views.eliminar_capitulo,
        name="eliminar_capitulo",
    ),

    # HTMX partidas
    path(
        "capitulos/<int:capitulo_pk>/partidas/anadir/",
        views.anadir_partida,
        name="anadir_partida",
    ),
    path("partidas/<int:partida_pk>/guardar/", views.guardar_partida, name="guardar_partida"),
    path(
        "partidas/<int:partida_pk>/eliminar/",
        views.eliminar_partida,
        name="eliminar_partida",
    ),

    # HTMX autocompletado desde catálogo
    path("partidas/autocompletar/", views.autocompletar_partida, name="autocompletar_partida"),
    path(
        "partidas/<int:partida_pk>/aplicar/<int:catalogo_pk>/",
        views.aplicar_sugerencia,
        name="aplicar_sugerencia",
    ),
]
