import logging
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .classifier import ButterflyModelError, predict_genus
from .forms import SightingImageForm
from .models import ButterflySighting


logger = logging.getLogger(__name__)


@login_required
def sighting_list(request):
    if request.method == "POST":
        form = SightingImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                genus, confidence = predict_genus(form.cleaned_data["image"])
            except ButterflyModelError:
                logger.exception(
                    "No se pudo clasificar la imagen del usuario %s",
                    request.user.pk,
                )
                messages.error(
                    request,
                    "No fue posible analizar la imagen. Inténtalo de nuevo más tarde.",
                )
            else:
                ButterflySighting.objects.create(
                    user=request.user,
                    image=form.cleaned_data["image"],
                    genus=genus,
                    confidence=confidence,
                )
                messages.success(request, f"Avistamiento registrado: {genus}.")
                return redirect("sighting_list")
    else:
        form = SightingImageForm()

    sightings = ButterflySighting.objects.filter(user=request.user)
    return render(
        request,
        "modelo/sighting_list.html",
        {"form": form, "sightings": sightings},
    )


@login_required
@require_POST
def delete_sighting(request, pk):
    sighting = get_object_or_404(ButterflySighting, pk=pk, user=request.user)
    sighting.image.delete(save=False)
    sighting.delete()
    messages.success(request, "El avistamiento fue eliminado.")
    return redirect("sighting_list")


@login_required
def sighting_image(request, pk):
    sighting = get_object_or_404(ButterflySighting, pk=pk, user=request.user)
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    content_type = content_types.get(
        Path(sighting.image.name).suffix.lower(),
        "application/octet-stream",
    )
    return FileResponse(sighting.image.open("rb"), content_type=content_type)
