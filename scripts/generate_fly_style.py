from pathlib import Path
import google.auth
from google import genai
from PIL import Image

def generate_fly() -> None:
    credentials, project = google.auth.default()
    if not project:
        raise ValueError("CRITICAL: GCP project not resolved from auth.")
        
    client = genai.Client(vertexai=True, project=project, location="us-central1")
    
    ref_path = Path(r"C:\Users\lukas\.gemini\antigravity\brain\84984e67-94b9-43d6-b4d9-c1207a264122\.user_uploaded\media_1791889789061_c27a194e.png")
    if not ref_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Reference image not found at {ref_path}")
        
    ref_img = Image.open(ref_path)
    
    prompt = (
        "Generate a minimalist black ink line art illustration of a tiny cute fly, facing forward. "
        "Strict art style to match the reference image: "
        "1. Exact same art style as the reference image: clean, simple, delicate black ink outline drawing. "
        "2. Minimalist character design: two simple black dot eyes, small cute features, sweet gentle expression. "
        "3. Pure white fill inside the drawing. Absolutely NO colors, NO grey tones, NO shading, NO hatching. "
        "4. Pure solid white background. No background elements, no frame, no ground, no shadows. "
        "5. Two delicate wings, rounded body, tiny legs. Clean and instantly recognizable as a cute little fly."
    )
    
    print("Calling gemini-2.5-flash-image with reference image...")
    res = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[ref_img, prompt]
    )
    
    raw_img: Image.Image | None = None
    for cand in res.candidates:
        if cand.content:
            for part in cand.content.parts:
                if part.inline_data and part.inline_data.data:
                    import io
                    raw_img = Image.open(io.BytesIO(part.inline_data.data)).convert("RGBA")
                    break
            if raw_img is not None:
                break
                
    if raw_img is None:
        raise RuntimeError("CRITICAL: No image returned by gemini-2.5-flash-image.")
        
    # Save raw generated image
    raw_path = Path("scripts/fly_raw.png")
    raw_img.save(raw_path)
    print(f"Saved raw image to {raw_path} with size {raw_img.size}")
    
    # Auto-crop non-white bounding box
    rgb = raw_img.convert("RGB")
    w, h = rgb.size
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b = rgb.getpixel((x, y))
            # If pixel is not white/near-white
            if r < 245 or g < 245 or b < 245:
                found = True
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    if not found:
        raise RuntimeError("CRITICAL: No non-white content detected in generated image.")
        
    pad = 8
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + pad + 1),
        min(h, max_y + pad + 1)
    )
    cropped = rgb.crop(crop_box)
    print(f"Cropped content bounding box: {crop_box}, size: {cropped.size}")
    
    # Target size for the fly on a 600x600 canvas (tiny fly: ~110px max dimension)
    target_fly_size = 110
    cw, ch = cropped.size
    scale = target_fly_size / max(cw, ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    scaled_fly = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Create 600x600 pure white canvas
    canvas = Image.new("RGB", (600, 600), (255, 255, 255))
    paste_x = (600 - new_w) // 2
    paste_y = (600 - new_h) // 2
    canvas.paste(scaled_fly, (paste_x, paste_y))
    
    canvas_path = Path("scripts/fly_600x600.png")
    canvas.save(canvas_path)
    print(f"Saved final 600x600 canvas to {canvas_path}")

if __name__ == "__main__":
    generate_fly()
