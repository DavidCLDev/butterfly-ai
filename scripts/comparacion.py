from pathlib import Path
import hashlib
from collections import defaultdict
import time

def calcular_hash_rapido(ruta_archivo):
    """Calcula el hash SHA-256 leyendo el archivo en bloques para optimizar memoria."""
    hasher = hashlib.sha256()
    try:
        with open(ruta_archivo, 'rb') as f:
            while chunk := f.read(65536):  # Bloques de 64KB para mayor velocidad en disco
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def buscar_duplicados_entre_carpetas(carpeta1, carpeta2):
    inicio = time.time()
    p1 = Path(carpeta1)
    p2 = Path(carpeta2)
    
    if not p1.exists() or not p1.is_dir() or not p2.exists() or not p2.is_dir():
        print("Error: Una o ambas rutas no son directorios válidos.")
        return

    print("Iniciando escaneo y cálculo de hashes de alta velocidad...")

    # Diccionarios para mapear hash -> lista de rutas
    # Usamos defaultdict para agrupar rápidamente
    hash_a_rutas_c1 = defaultdict(list)
    hash_a_rutas_c2 = defaultdict(list)

    # 1. Escanear Carpeta 1
    total_c1 = 0
    for archivo in p1.rglob('*'):  # rglob busca también en subcarpetas si lo deseas, o usa iterdir() si es solo la raíz
        if archivo.is_file():
            total_c1 += 1
            h = calcular_hash_rapido(archivo)
            if h:
                hash_a_rutas_c1[h].append(archivo)

    # 2. Escanear Carpeta 2
    total_c2 = 0
    for archivo in p2.rglob('*'):
        if archivo.is_file():
            total_c2 += 1
            h = calcular_hash_rapido(archivo)
            if h:
                hash_a_rutas_c2[h].append(archivo)

    # 3. Cruzar información (Buscar qué hashes de C1 existen en C2)
    coincidencias = 0
    
    print("\n" + "=" * 70)
    print(f"ANALIZANDO {p2.name}")
    print("=" * 70)
    print(f"Total analizados en Carpeta 1: {total_c1} archivos")
    print(f"Total analizados en Carpeta 2: {total_c2} archivos\n")

    for h, rutas1 in hash_a_rutas_c1.items():
        if h in hash_a_rutas_c2:
            coincidencias += 1
            rutas2 = hash_a_rutas_c2[h]
            
            print(f"Coincidencia #{coincidencias} (Hash ID: {h[:10]}...)")
            print("  En Carpeta 1:")
            for r in rutas1:
                print(f"    -> {r.name}  (Ruta: {r})")
            print("  En Carpeta 2:")
            for r in rutas2:
                print(f"    -> {r.name}  (Ruta: {r})")
            print("-" * 70)

    if coincidencias == 0:
        print("No se encontraron archivos con contenido idéntico entre ambas carpetas.")
    else:
        print(f"\nProceso finalizado. Se encontraron {coincidencias} grupos de archivos idénticos.")
    
    print(f"Tiempo total transcurrido: {time.time() - inicio:.2f} segundos.")
    print("=" * 70)

if __name__ == "__main__":
    # --- CONFIGURACIÓN DE RUTAS ---
    root = Path(__file__).resolve().parents[1] / "data"
    dirs = [root / "train", root / "val"]

    for d in dirs[0].iterdir():
        if d.is_dir():
            buscar_duplicados_entre_carpetas(dirs[0] / d.name, dirs[1] / d.name)