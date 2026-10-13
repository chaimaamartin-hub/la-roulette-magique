import io
import time
from pathlib import Path
import google.auth
from google import genai
from PIL import Image

ANIMALS: list[dict[str, str | int]] = [
    {
        "score": 0,
        "name": "ant",
        "filename": "score_0_ant.png",
        "size": 80,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a tiny cute ant, facing forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines with organic hand-drawn feel. "
            "2. Minimalist design: two cute black dot eyes, small round head, tiny antennae, segmented body, delicate little legs. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor, no shadows."
        ),
    },
    {
        "score": 1,
        "name": "fly",
        "filename": "score_1_fly.png",
        "size": 120,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a tiny cute fly, facing forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink outline drawing. "
            "2. Two simple black dot eyes, small cute features, sweet gentle expression. "
            "3. Pure white fill inside. Absolutely NO colors, NO grey tones, NO shading. "
            "4. Pure solid white background. Two delicate wings, rounded body, tiny legs."
        ),
    },
    {
        "score": 2,
        "name": "frog",
        "filename": "score_2_frog.png",
        "size": 180,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute little frog sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Two simple black dot eyes on top of the head, gentle subtle smile, front legs resting between sitting hind legs. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor, no lily pad."
        ),
    },
    {
        "score": 3,
        "name": "duck",
        "filename": "score_3_duck.png",
        "size": 230,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute little duckling / duck sitting upright facing forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Two simple black dot eyes, cute simple rounded beak/bill, small wings at sides, gentle sweet expression. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no pond, no water."
        ),
    },
    {
        "score": 4,
        "name": "bunny",
        "filename": "score_4_bunny.png",
        "size": 280,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute little rabbit / bunny sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Two long upright perked ears, two simple black dot eyes, small black nose, two front paws in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 5,
        "name": "cat",
        "filename": "score_5_cat.png",
        "size": 340,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute little cat / kitten sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Two pointed triangular ears, two simple black dot eyes, tiny black nose with whiskers, front paws together in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 6,
        "name": "dog",
        "filename": "score_6_dog.png",
        "size": 400,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute friendly dog sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines, exactly matching the reference dog. "
            "2. Floppy folded ears framing the head, two simple black dot eyes, small black nose, front paws straight in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 7,
        "name": "fox",
        "filename": "score_7_fox.png",
        "size": 450,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute fox sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Triangular ears, two simple black dot eyes, small black nose, bushy tail curled neatly at side, front paws in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 8,
        "name": "sheep",
        "filename": "score_8_sheep.png",
        "size": 500,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute fluffy sheep sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Round cloud-like fluffy wool outline, gentle cute face, two simple black dot eyes, cute little ears. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 9,
        "name": "lion",
        "filename": "score_9_lion.png",
        "size": 550,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a cute lion cub / baby lion sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Soft round cloud-like mane framing the head, round ears, two simple black dot eyes, black nose, front paws in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
    {
        "score": 10,
        "name": "bear",
        "filename": "score_10_bear.png",
        "size": 590,
        "prompt": (
            "Generate a minimalist black ink line art illustration of a big friendly gentle bear sitting upright facing directly forward. "
            "Strict art style to match the reference image: "
            "1. Clean, simple, delicate black ink contour lines. "
            "2. Round ears on top, big round friendly body, two simple black dot eyes, black nose, front paws in front. "
            "3. Pure white fill inside. Absolutely NO color, NO grey tones, NO shading. "
            "4. Pure solid white background. No background elements, no floor."
        ),
    },
]


def process_image(raw_img: Image.Image, target_size: int, output_path: Path) -> None:
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
        raise RuntimeError(f"CRITICAL: No non-white content detected in generated image for {output_path.name}")

    pad = 8
    crop_box = (
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + pad + 1),
        min(h, max_y + pad + 1),
    )
    cropped = rgb.crop(crop_box)
    cw, ch = cropped.size
    scale = target_size / max(cw, ch)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (600, 600), (255, 255, 255))
    paste_x = (600 - new_w) // 2
    paste_y = (600 - new_h) // 2
    canvas.paste(scaled, (paste_x, paste_y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    print(f"Successfully created {output_path} (target size: {target_size}px, cropped: {cw}x{ch})")


def main() -> None:
    credentials, project = google.auth.default()
    if not project:
        raise ValueError("CRITICAL: GCP project not resolved from auth.")

    client = genai.Client(vertexai=True, project=project, location="us-central1")
    ref_path = Path(r"C:\Users\lukas\.gemini\antigravity\brain\84984e67-94b9-43d6-b4d9-c1207a264122\style_reference.png")
    if not ref_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Reference image not found at {ref_path}")
    ref_img = Image.open(ref_path)

    out_dir = Path("assets/images/animals")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Note: Fly (score 1) already has raw generated image from previous turn!
    fly_raw_path = Path("scripts/fly_raw.png")

    for item in ANIMALS:
        score = int(item["score"])
        name = str(item["name"])
        filename = str(item["filename"])
        target_size = int(item["size"])
        prompt = str(item["prompt"])
        out_file = out_dir / filename

        print(f"\n--- Generating score {score}: {name} ({filename}, target={target_size}px) ---")

        if name == "fly" and fly_raw_path.is_file():
            print("Reusing existing fly_raw.png...")
            raw_img = Image.open(fly_raw_path)
            process_image(raw_img, target_size, out_file)
            continue

        retries = 3
        while retries > 0:
            try:
                res = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[ref_img, prompt],
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
                    raise RuntimeError(f"No image returned for {name}")

                # Save raw backup in scripts/raw_{name}.png
                raw_img.save(f"scripts/raw_{name}.png")
                process_image(raw_img, target_size, out_file)
                break
            except Exception as e:
                retries -= 1
                print(f"Error generating {name}: {type(e).__name__}: {e}. Retries left: {retries}")
                time.sleep(2)
                if retries == 0:
                    raise

    print("\nAll 11 animals successfully generated and placed in assets/images/animals/!")


if __name__ == "__main__":
    main()
