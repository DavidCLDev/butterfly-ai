import csv
from collections import Counter
from pathlib import Path

def resumir_imagenes_std():
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    csv_path = project_root / "data" / "registro_imagenes.csv"

    if not csv_path.exists():
        print(f"Error: El archivo '{csv_path.name}' no existe.")
        return

    conteo = Counter()
    total_registros = 0

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conteo[row["especie"]] += 1
            total_registros += 1

    print("\n--- RESUMEN DE IMÁGENES POR ESPECIE ---")
    # Imprimir alineado en formato de columna
    for especie, total in conteo.most_common():
        print(f"{especie:<30}: {total} imágenes")
    print("---------------------------------------")
    print(f"TOTAL GENERAL: {total_registros} imágenes.\n")

if __name__ == "__main__":
    resumir_imagenes_std()