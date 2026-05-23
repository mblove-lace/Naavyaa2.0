from PIL import Image
import os

folder_path = r"C:\Users\moith\OneDrive\Heeya Software Dev Learnings\Full Stack Web Dev Knowledge\Full Stack Projects\Full Stack Projects- Naavyaa with template k\Product Images\Products\Hand-Block\New folder\titalee_jpeg"

new_size = (1200, 1600)

for filename in os.listdir(folder_path):
    if filename.lower().endswith((".jpg", ".jpeg")):

        old_path = os.path.join(folder_path, filename)
        new_filename = os.path.splitext(filename)[0] + ".jpg"
        new_path = os.path.join(folder_path, new_filename)

        try:
            # Open and convert (important for saving as JPEG)
            img = Image.open(old_path).convert("RGB")

            # Resize WITHOUT distortion
            img.thumbnail(new_size, Image.LANCZOS)

            # Create white background
            new_img = Image.new("RGB", new_size, (255, 255, 255))

            # Center the image
            x = (new_size[0] - img.size[0]) // 2
            y = (new_size[1] - img.size[1]) // 2

            new_img.paste(img, (x, y))

            # Save as JPEG
            new_img.save(new_path, "JPEG", quality=90, optimize=True)

            # Delete old .jpeg file if needed
            if old_path != new_path:
                os.remove(old_path)

            print(f"✅ Done: {filename}")

        except Exception as e:
            print(f"❌ Error: {filename} → {e}")