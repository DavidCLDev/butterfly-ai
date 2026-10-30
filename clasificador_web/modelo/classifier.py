import ast
from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps
from django.conf import settings


class ButterflyModelError(Exception):
    pass


@lru_cache(maxsize=1)
def _get_session():
    model_path = Path(settings.BASE_DIR) / "model" / "best.onnx"
    try:
        return ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"],
        )
    except (OSError, ort.OrtError) as exc:
        raise ButterflyModelError("No se pudo cargar el modelo ONNX.") from exc


def _get_class_names(session):
    metadata_names = session.get_modelmeta().custom_metadata_map.get("names")
    if not metadata_names:
        raise ButterflyModelError("El modelo no contiene nombres de clases.")

    try:
        names_by_id = ast.literal_eval(metadata_names)
        class_names = [names_by_id[index] for index in range(len(names_by_id))]
    except (SyntaxError, ValueError, KeyError, TypeError) as exc:
        raise ButterflyModelError("Los nombres de clase del modelo no son válidos.") from exc

    if not all(isinstance(name, str) and name for name in class_names):
        raise ButterflyModelError("Los nombres de clase del modelo no son válidos.")
    return class_names


def predict_genus(image_file):
    session = _get_session()
    model_input = session.get_inputs()[0]
    height, width = model_input.shape[2:4]
    if not isinstance(height, int) or not isinstance(width, int):
        raise ButterflyModelError("El modelo requiere un tamaño de imagen fijo.")

    try:
        image_file.seek(0)
        with Image.open(image_file) as image:
            image = ImageOps.fit(
                image.convert("RGB"),
                (width, height),
                method=Image.Resampling.BILINEAR,
            )
            tensor = np.asarray(image, dtype=np.float32) / 255.0
        image_file.seek(0)
        tensor = np.transpose(tensor, (2, 0, 1))[np.newaxis, ...]
        output = session.run(
            None,
            {model_input.name: tensor},
        )[0]
    except (OSError, ValueError, ort.OrtError) as exc:
        raise ButterflyModelError("No se pudo clasificar la imagen.") from exc

    scores = np.asarray(output).reshape(-1)
    class_names = _get_class_names(session)
    if scores.size != len(class_names) or not np.isfinite(scores).all():
        raise ButterflyModelError("La salida del modelo no coincide con sus clases.")

    best_index = int(np.argmax(scores))
    return class_names[best_index], float(scores[best_index]) * 100
