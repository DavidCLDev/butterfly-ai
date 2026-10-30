from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError


class SightingImageForm(forms.Form):
    image = forms.ImageField(
        label="Fotografía",
        help_text="Formatos JPG, PNG o WebP. Tamaño máximo: 10 MB.",
    )

    def clean_image(self):
        image = self.cleaned_data["image"]
        if image.size > 10 * 1024 * 1024:
            raise ValidationError("La imagen no puede superar los 10 MB.")
        if image.image.width * image.image.height > 25_000_000:
            raise ValidationError("La imagen no puede superar los 25 megapíxeles.")
        valid_extensions = {
            "JPEG": {".jpg", ".jpeg"},
            "PNG": {".png"},
            "WEBP": {".webp"},
        }
        extension = Path(image.name).suffix.lower()
        if extension not in valid_extensions.get(image.image.format, set()):
            raise ValidationError("El formato debe ser JPG, PNG o WebP.")
        return image
