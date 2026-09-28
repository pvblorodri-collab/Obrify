from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Obra


@login_required
def lista_obras(request):
    obras = Obra.objects.filter(organizacion=request.user.organizacion).select_related("cliente")
    return render(request, "projects/lista.html", {"obras": obras})


@login_required
def detalle_obra(request, pk: int):
    obra = get_object_or_404(
        Obra.objects.select_related("cliente"),
        pk=pk,
        organizacion=request.user.organizacion,
    )
    return render(request, "projects/detalle.html", {"obra": obra})
