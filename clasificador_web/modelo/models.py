from django.conf import settings
from django.db import models


class ButterflySighting(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="butterfly_sightings",
    )
    image = models.ImageField(upload_to="avistamientos/%Y/%m/")
    genus = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.genus} - {self.user}"
