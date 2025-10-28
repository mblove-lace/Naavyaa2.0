import os
from PIL import Image
import pillow_heif

# Register HEIF format
pillow_heif.register_heif_opener()

# Set input/output folders
input_folder = r"D:\naavyaa website\Product Images\Products\Saree"
output_folder = r"D:\naavyaa website\Product Images\Products\Saree"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder) :
    file_lower = filename.lower()

    if file_lower.endswith(".heic") or file_lower.endswith(".png"):
        source_path = os.path.join(input_folder, filename)
        jpg_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")

        try:
            image = Image.open(source_path).convert("RGB")
            image.save(jpg_path, "JPEG", quality=100)
            print(f"✅ Converted: {filename}→ {os.path.basename(jpg_path)}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")
