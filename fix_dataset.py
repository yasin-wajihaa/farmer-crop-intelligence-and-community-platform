import os
from PIL import Image

DATASET = "/home/maxwell/plant_doctor_backend/data/plantvillage/color"

print("Cleaning dataset at:", DATASET)

fixed = 0
deleted = 0

for root, dirs, files in os.walk(DATASET):
    for file in files:

        path = os.path.join(root, file)

        try:
            img = Image.open(path)

            # FORCE RGB
            img = img.convert("RGB")

            # FORCE SIZE
            img = img.resize((128, 128))

            # overwrite same file
            img.save(path, "JPEG", quality=95)

            fixed += 1

        except Exception as e:
            print("Deleting corrupted:", path)
            os.remove(path)
            deleted += 1

print("DONE")
print("Fixed images:", fixed)
print("Deleted images:", deleted)
