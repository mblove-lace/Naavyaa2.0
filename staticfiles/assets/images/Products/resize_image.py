from PIL import Image
import os

# Folder containing your JPG images
folder_path = r"D:\naavyaa website\Product Images\Products\HAKOBA_jpg"

# Desired size (width, height)
new_size = (570, 720)

# Resize all JPG files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".jpg"):
        img_path = os.path.join(folder_path, filename)
        try:
            img = Image.open(img_path)

            # Resize and save (overwrite original)
            img_resized = img.resize(new_size, Image.LANCZOS)  # High quality resize
            img_resized.save(img_path, "JPEG", quality=95)

            print(f"✅ Resized: {filename} to {new_size}")
        except Exception as e:
            print(f"❌ Failed to resize {filename}: {e}")
