from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_obras, name="lista_obras"),
    path("<int:pk>/", views.detalle_obra, name="detalle_obra"),
]
