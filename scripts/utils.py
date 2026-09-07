import os
from pathlib import Path

def get_images_ids(path: Path) -> set:

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
    ''' Archivos sin procesar '''
    unprocessed_files = {
        int(os.path.splitext(file)[0].split("_")[1])
        for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))
    }

    ''' Archivos procesados '''
    processed_files = {
        int(os.path.splitext(file)[0].split("_")[1])
        for file in os.listdir(path.resolve() / "processed")
    }
    
    ''' Archivos eliminados '''
    delete_files = {
        int(os.path.splitext(file)[0].split("_")[1])
        for file in os.listdir(path.resolve().parents[0] / "DELETE")
        if path.name in file
    }
    
    photo_ids = unprocessed_files.union(processed_files, delete_files)

    return photo_ids

if __name__ == "__main__":
    DATA = Path(__file__).resolve().parents[1] / "data"

    images_per_species = []

    for species in os.listdir(DATA):
        if species == "DELETE":
            continue
        ids = get_images_ids(Path(f"data/{species}"))
        images_per_species.append(len(ids))
        print(species, len(ids))
    print("Total:", sum(images_per_species))