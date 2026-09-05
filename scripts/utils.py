import os

def get_images_ids(path):
    files = os.listdir(path)

    photo_ids = {
        int(os.path.splitext(file)[0].split("_")[1])
        for file in files
    }

    return photo_ids

if __name__ == "__main__":
    ids = get_images_ids()
    print(ids)