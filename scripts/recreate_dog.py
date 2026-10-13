import io
from pathlib import Path
import google.auth
from google import genai
from PIL import Image

def recreate_dog() -> None:
    credentials, project = google.auth.default()
    if not project:
        raise ValueError("CRITICAL: GCP project not resolved from auth.")

    client = genai.Client(vertexai=True, project=project, location="us-central1")
    fox_path = Path("assets/images/animals/score_7_fox.png")
    if not fox_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Fox template image not found at {fox_path}")
    fox_img = Image.open(fox_path)

    prompt = (
        "Generate a cute friendly dog sitting upright facing directly forward, using the provided fox image as the exact structural and stylistic template: "
        "1. Exact same art style and composition as the template image: clean, crisp black ink line art, pure white fill inside, no color, no shading. "
        "2. Perfectly centered front-facing symmetrical sitting pose: two front paws planted straight down in the center, sitting hind legs on both sides. "
        "3. Animal features changed to a dog/puppy: cute floppy or folded dog ears, gentle rounded dog head, cute black dot eyes with subtle eyebrows, black dog nose, friendly mouth, short wagging dog tail at the side or tucked. "
        "4. Pure solid white background with no background elements, no floor, no shadows."
    )

    print("Generating dog with fox template via gemini-2.5-flash-image...")
    res = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[fox_img, prompt],
    )

    raw_img = None
    for cand in res.candidates:
        if cand.content:
            for part in cand.content.parts:
                if part.inline_data and part.inline_data.data:
                    raw_img = Image.open(io.BytesIO(part.inline_data.data))
                    break
        if raw_img is not None:
            break

    if raw_img is None:
        raise RuntimeError("CRITICAL: No image returned by gemini-2.5-flash-image.")

    raw_img.save("scripts/raw_dog_new.png")

    # Crop content
    rgb = raw_img.convert("RGB")
    w, h = rgb.size
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b = rgb.getpixel((x, y))
            if r < 245 or g < 245 or b < 245:
                found = True
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y

    if not found:
        raise RuntimeError("CRITICAL: No content found in generated dog image.")

    pad = 8
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + pad + 1),
        min(h, max_y + pad + 1),
    )
    cropped = rgb.crop(crop_box)
    cw, ch = cropped.size

    # Dog target size is 400px on 600x600 canvas
    target_size = 400
    scale = target_size / max(cw, ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (600, 600), (255, 255, 255))
    paste_x = (600 - new_w) // 2
    paste_y = (600 - new_h) // 2
    canvas.paste(scaled, (paste_x, paste_y))

    out_path = Path("assets/images/animals/score_6_dog.png")
    canvas.save(out_path)
    canvas.save("scripts/dog_new_600x600.png")
    print(f"Successfully recreated {out_path} (target size: {target_size}px, cropped: {cw}x{ch})")

if __name__ == "__main__":
    recreate_dog()
