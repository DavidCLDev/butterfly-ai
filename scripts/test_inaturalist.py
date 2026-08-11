from utils import get_images_ids

from pathlib import Path
from urllib.parse import urlparse

import requests


API_URL = "https://api.inaturalist.org/v1/observations"
SPECIES = [
    "Danaus plexippus",
    "Heliconius erato",
    "Morpho helenor",
    "Papilo Polyxenes",
    "Dryas iulia",
    "Ascia monuste",
    "Phoebis sennae",
    "Vanessa virginiensis",
    "Battus polydamas",
    "Anartia amathea"
]
COLOMBIA_PLACE_ID = 7196
RESULTS_LIMIT = 2
REQUEST_TIMEOUT_SECONDS = 20
OUTPUT_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "raw" / "inaturalist"


def location_from(observation: dict) -> str:
    """Devuelve una ubicación legible sin asumir que la observación tiene coordenadas."""
    if observation.get("place_guess"):
        return observation["place_guess"]

    coordinates = observation.get("geojson", {}).get("coordinates")
    if coordinates and len(coordinates) >= 2:
        longitude, latitude = coordinates[:2]
        return f"{latitude}, {longitude}"
    return "No disponible"


def photo_url_from(observation: dict) -> str | None:
    """Obtiene una URL de tamaño grande de la primera foto, si existe."""
    photos = observation.get("photos") or []
    if not photos or not photos[0].get("url"):
        return None
    return photos[0]["url"].replace("square", "large")


def unused_path(directory: Path, observation_id: int, photo_url: str) -> Path:
    """Crea un nombre de archivo que no sobrescribe descargas anteriores."""
    suffix = Path(urlparse(photo_url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    candidate = directory / f"observation_{observation_id}{suffix}"
    number = 1
    while candidate.exists():
        candidate = directory / f"observation_{observation_id}_{number}{suffix}"
        number += 1
    return candidate


def download_photo(observation_id: int, photo_url: str) -> Path:
    """Descarga una sola fotografía y devuelve la ruta donde se guardó."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = unused_path(OUTPUT_DIRECTORY, observation_id, photo_url)

    response = requests.get(photo_url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def main() -> None:
    images_ids = get_images_ids()
    print("Consultando iNaturalist...")
    parameters = {
        "place_id": COLOMBIA_PLACE_ID,
        "per_page": RESULTS_LIMIT,
        "order_by": "random",
        "order": "desc",
    }
    results = []
    project_root = Path(__file__).resolve().parents[1]

    try:
        for taxon_name in SPECIES:
            parameters["taxon_name"] = taxon_name
            response = requests.get(API_URL, params=parameters, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            result = response.json().get("results", [])
            for i, observation in enumerate(result):
                if observation.get("id", "Desconocido") in images_ids:
                    result.pop(i)
            results.append(result)
    except requests.RequestException as error:
        print(f"No fue posible consultar la API: {error}")
        return
    except ValueError:
        print("La API respondió con contenido que no es JSON válido.")
        return

    if not results:
        print("No hubo resultados para la especie y ubicación seleccionadas.")
        return

    first_photo: tuple[int, str] | None = None
    for observations in results:
        for observation in observations:
            observation_id = observation.get("id", "Desconocido")
            taxon = observation.get("taxon") or {}
            scientific_name = taxon.get("name", "No identificada")
            photos = observation.get("photos") or []
            photo_url = photo_url_from(observation)

            print(f"\nObservación: {observation_id}")
            print(f"Especie: {scientific_name}")
            print(f"Fecha: {observation.get('observed_on') or 'No disponible'}")
            print(f"Ubicación: {location_from(observation)}")
            print(f"Fotografías: {len(photos)}")
            print(f"URL: {photo_url or 'No disponible'}")

            if isinstance(observation_id, int) and photo_url:
                try:
                    print("Descargando...")
                    saved_path = download_photo(observation_id, photo_url)
                    print("Imagen guardada en:")
                    print(saved_path.relative_to(project_root))
                except requests.RequestException as error:
                    print(f"No fue posible descargar la fotografía: {error}")
                    return
                except OSError as error:
                    print(f"No fue posible guardar la fotografía: {error}")
                    return

            if first_photo is None and isinstance(observation_id, int) and photo_url:
                first_photo = (observation_id, photo_url)

    if first_photo is None:
        print("\nNinguna de las observaciones contiene una fotografía descargable.")
        return


if __name__ == "__main__":
    main()
