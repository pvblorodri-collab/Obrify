from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.projects.models import Obra


@login_required
def home(request):
    obras = Obra.objects.filter(organizacion=request.user.organizacion).order_by("-creada_en")[:10]
    return render(
        request,
        "home.html",
        {"obras": obras},
    )
