import io
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tts_generator import TTSRequest, resolve_project_id
import google.auth
from google.auth.transport.requests import Request
import requests
import base64

ANIMAL_AUDIO_MANIFEST = [
    {
        "score": 0,
        "name": "ant",
        "voice": "Aoede",
        "text": "Hop, hop ! Courage, réessaie !",
        "style": "Warm, energetic preschool teacher imitating tiny brisk ant footsteps then encouraging cheer: Hop, hop ! Courage, réessaie !",
    },
    {
        "score": 1,
        "name": "fly",
        "voice": "Aoede",
        "text": "Bzz, bzz ! Continue, tu peux le faire !",
        "style": "Cheerful preschool teacher imitating playful buzzy fly then encouraging cheer: Bzz, bzz ! Continue, tu peux le faire !",
    },
    {
        "score": 2,
        "name": "frog",
        "voice": "Puck",
        "text": "Coâ, coâ ! C'est un bon début !",
        "style": "Friendly preschool teacher imitating cute frog croak then positive encouragement: Coâ, coâ ! C'est un bon début !",
    },
    {
        "score": 3,
        "name": "duck",
        "voice": "Aoede",
        "text": "Coin, coin ! Tu apprends vite !",
        "style": "Cheerful preschool teacher imitating playful duck quack then positive encouragement: Coin, coin ! Tu apprends vite !",
    },
    {
        "score": 4,
        "name": "bunny",
        "voice": "Aoede",
        "text": "Hop, hop ! Continue comme ça !",
        "style": "Cheerful preschool teacher imitating cute bunny hops then energetic encouragement: Hop, hop ! Continue comme ça !",
    },
    {
        "score": 5,
        "name": "cat",
        "voice": "Aoede",
        "text": "Miaou, miaou ! C'est super !",
        "style": "Warm preschool teacher imitating sweet kitten meow then enthusiastic cheer: Miaou, miaou ! C'est super !",
    },
    {
        "score": 6,
        "name": "dog",
        "voice": "Puck",
        "text": "Ouaf, ouaf ! Tu y es presque !",
        "style": "Cheerful preschool teacher imitating energetic happy puppy bark then encouraging cheer: Ouaf, ouaf ! Tu y es presque !",
    },
    {
        "score": 7,
        "name": "fox",
        "voice": "Puck",
        "text": "Yap, yap ! Bien joué, petit malin !",
        "style": "Playful preschool teacher imitating clever little fox yip then cheerful praise: Yap, yap ! Bien joué, petit malin !",
    },
    {
        "score": 8,
        "name": "sheep",
        "voice": "Aoede",
        "text": "Bêê, bêê ! Formidable !",
        "style": "Warm preschool teacher imitating friendly gentle sheep bleat then celebratory praise: Bêê, bêê ! Formidable !",
    },
    {
        "score": 9,
        "name": "lion",
        "voice": "Puck",
        "text": "Wrrroaaarrr ! Très bien !",
        "style": "Deep ferocious but child-friendly lion roar and loud rumble: Wrrroaaarrr! followed by celebratory praise: Très bien !",
    },
    {
        "score": 10,
        "name": "bear",
        "voice": "Puck",
        "text": "Grroaar ! Parfait !",
        "style": "Warm preschool teacher imitating friendly gentle bear growl and roar then celebratory praise: Grroaar ! Parfait !",
    },
]


def synthesize_and_save(
    text: str,
    voice_name: str,
    style_prompt: str,
    output_path: Path,
) -> None:
    project_id = resolve_project_id()
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())

    url = (
        f"https://aiplatform.googleapis.com/v1/projects/{project_id}/"
        f"locations/global/publishers/google/models/gemini-3.8-flash-tts:generateContent"
    )
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
    user_part = {"text": text, "speechMetadata": {"style": style_prompt}}
    payload = {
        "contents": [{"role": "user", "parts": [user_part]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
            },
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"TTS API error ({resp.status_code}): {resp.text}")

    data = resp.json()
    raw_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    wav_bytes = base64.b64decode(raw_b64)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_wav = output_path.with_suffix(".tmp.wav")
    temp_wav.write_bytes(wav_bytes)

    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
    # Direct high-quality conversion to MP3 without artificial silence removal
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(temp_wav),
        "-ar",
        "44100",
        "-b:a",
        "192k",
        str(output_path),
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {res.stderr}")
    finally:
        if temp_wav.is_file():
            temp_wav.unlink()


def get_duration(mp3_path: Path) -> float:
    ffprobe_bin = shutil.which("ffprobe") or "ffprobe"
    cmd = [
        ffprobe_bin,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(mp3_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def main() -> None:
    dest_dir = Path("assets/audio/animals")
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("\n==========================================")
    print(f"Generating curated animal sounds -> {dest_dir}")
    print("==========================================")

    for item in ANIMAL_AUDIO_MANIFEST:
        score = item["score"]
        name = item["name"]
        voice_name = item["voice"]
        filename = f"score_{score}_{name}.mp3"
        out_file = dest_dir / filename

        print(f"Generating score {score}: {name} ({voice_name})...")
        retries = 3
        while retries > 0:
            try:
                synthesize_and_save(
                    text=item["text"],
                    voice_name=voice_name,
                    style_prompt=item["style"],
                    output_path=out_file,
                )
                dur = get_duration(out_file)
                print(f"  -> Saved {out_file.name}: duration = {dur:.2f}s (voice: {voice_name})")
                break
            except Exception as e:
                retries -= 1
                print(f"  -> Error: {e}, retries left: {retries}")
                time.sleep(2)
                if retries == 0:
                    raise

    # Clean up redundant subdirectories if present
    for sub in ["voice_female", "voice_male"]:
        sub_p = dest_dir / sub
        if sub_p.is_dir():
            shutil.rmtree(sub_p)
            print(f"Removed legacy subfolder: {sub_p}")

    print("\nAll 11 curated animal audio files successfully generated directly in assets/audio/animals/!")


if __name__ == "__main__":
    main()

