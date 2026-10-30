from django.urls import path

from . import views

urlpatterns = [
    path("", views.sighting_list, name="sighting_list"),
    path(
        "avistamientos/<int:pk>/eliminar/",
        views.delete_sighting,
        name="delete_sighting",
    ),
    path(
        "avistamientos/<int:pk>/imagen/",
        views.sighting_image,
        name="sighting_image",
    ),
]