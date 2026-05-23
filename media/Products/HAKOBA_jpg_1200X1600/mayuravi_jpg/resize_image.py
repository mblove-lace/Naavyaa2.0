from PIL import Image, ImageOps
import os

folder_path = r"C:\Users\moith\OneDrive\Heeya Software Dev Learnings\Full Stack Web Dev Knowledge\Full Stack Projects\Full Stack Projects- Naavyaa with template k\Product Images\Products\HAKOBA_jpg_1200X1600\mayuravi_jpg"

target_size = (1200, 1600)

for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):

        old_path = os.path.join(folder_path, filename)
        new_filename = os.path.splitext(filename)[0] + ".jpg"
        new_path = os.path.join(folder_path, new_filename)

        try:
            img = Image.open(old_path).convert("RGB")

            # Resize + crop (NO distortion, NO white space)
            final_img = ImageOps.fit(
                img,
                target_size,
                Image.LANCZOS,
                centering=(0.5, 0.5)  # center crop
            )

            final_img.save(new_path, "JPEG", quality=90, optimize=True)

            print(f"✅ Done: {filename}")

        except Exception as e:
            print(f"❌ Error: {filename} → {e}")