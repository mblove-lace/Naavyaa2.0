from PIL import Image
import os

# Folder containing your JPG images
folder_path = r"C:\Users\moith\OneDrive\Heeya Software Dev Learnings\Full Stack Web Dev Knowledge\Full Stack Projects\Full Stack Projects- Naavyaa with template k\Product Images\Products\Hand-Block"

# Desired size (width, height)
new_size = (1200, 1600)

# Resize all JPEG files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".jpeg"):
        img_path = os.path.join(folder_path, filename)
        try:
            img = Image.open(img_path)

            # Resize and save (overwrite original)
            img_resized = img.resize(new_size, Image.LANCZOS)  # High quality resize
            img_resized.save(img_path, "png", quality=95)

            print(f"✅ Resized: {filename} to {new_size}")
        except Exception as e:
            print(f"❌ Failed to resize {filename}: {e}")
