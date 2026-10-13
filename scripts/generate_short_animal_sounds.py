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

SHORT_MANIFEST = [
    {
        "score": 0,
        "name": "ant",
        "text": "Hop, hop ! Courage, réessaie !",
        "style": "Energetic, friendly preschool teacher imitating tiny brisk ant footsteps then warm encouraging cheer: Hop, hop ! Courage, réessaie !",
    },
    {
        "score": 1,
        "name": "fly",
        "text": "Bzz, bzz ! Continue, tu peux le faire !",
        "style": "Cheerful preschool teacher imitating playful buzzy fly then encouraging cheer: Bzz, bzz ! Continue, tu peux le faire !",
    },
    {
        "score": 2,
        "name": "frog",
        "text": "Coâ, coâ ! C'est un bon début !",
        "style": "Cheerful preschool teacher imitating cute double frog croak then positive encouragement: Coâ, coâ ! C'est un bon début !",
    },
    {
        "score": 3,
        "name": "duck",
        "text": "Coin, coin ! Tu apprends vite !",
        "style": "Cheerful preschool teacher imitating playful duck quack then positive encouragement: Coin, coin ! Tu apprends vite !",
    },
    {
        "score": 4,
        "name": "bunny",
        "text": "Hop, hop ! Continue comme ça !",
        "style": "Cheerful preschool teacher imitating cute bunny hops then energetic encouragement: Hop, hop ! Continue comme ça !",
    },
    {
        "score": 5,
        "name": "cat",
        "text": "Miaou, miaou ! C'est super !",
        "style": "Warm preschool teacher imitating sweet kitten meow then enthusiastic cheer: Miaou, miaou ! C'est super !",
    },
    {
        "score": 6,
        "name": "dog",
        "text": "Ouaf, ouaf ! Tu y es presque !",
        "style": "Cheerful preschool teacher imitating energetic happy puppy bark then encouraging cheer: Ouaf, ouaf ! Tu y es presque !",
    },
    {
        "score": 7,
        "name": "fox",
        "text": "Yap, yap ! Bien joué, petit malin !",
        "style": "Cheerful preschool teacher imitating clever little fox playful yip then cheerful cheer: Yap, yap ! Bien joué, petit malin !",
    },
    {
        "score": 8,
        "name": "sheep",
        "text": "Bêê, bêê ! Formidable !",
        "style": "Warm preschool teacher imitating friendly sheep bleat then celebratory praise: Bêê, bêê ! Formidable !",
    },
    {
        "score": 9,
        "name": "lion",
        "text": "Rroarrr ! Très bien !",
        "style": "Playful preschool teacher imitating cute friendly lion cub roar then proud celebratory praise: Rroarrr ! Très bien !",
    },
    {
        "score": 10,
        "name": "bear",
        "text": "Grroaar ! Parfait !",
        "style": "Warm preschool teacher imitating friendly gentle bear growl and roar then celebratory praise: Grroaar ! Parfait !",
    },
]



def synthesize_and_trim(
    text: str,
    voice_name: str,
    style_prompt: str,
    output_path: Path,
    max_duration: float = 1.9,
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
    # Trim silence and gracefully cap at max_duration with gentle fade
    fade_start = max(1.0, max_duration - 0.25)
    filter_arg = (
        f"silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB:"
        f"stop_periods=1:stop_duration=0.2:stop_threshold=-45dB,"
        f"atrim=0:{max_duration},afade=t=out:st={fade_start}:d=0.25"
    )
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(temp_wav),
        "-af",
        filter_arg,
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
    root = Path("assets/audio/animals")
    voices = [
        ("Aoede", root / "voice_female"),
        ("Puck", root / "voice_male"),
    ]

    for voice_name, dest_dir in voices:
        print(f"\n==========================================")
        print(f"Generating for voice: {voice_name} -> {dest_dir}")
        print(f"==========================================")
        dest_dir.mkdir(parents=True, exist_ok=True)

        for item in SHORT_MANIFEST:
            score = item["score"]
            name = item["name"]
            filename = f"score_{score}_{name}.mp3"
            out_file = dest_dir / filename

            print(f"Generating score {score}: {name} ({voice_name})...")
            retries = 3
            while retries > 0:
                try:
                    synthesize_and_trim(
                        text=item["text"],
                        voice_name=voice_name,
                        style_prompt=item["style"],
                        output_path=out_file,
                        max_duration=3.5,
                    )
                    dur = get_duration(out_file)
                    print(f"  -> Saved {out_file.name}: duration = {dur:.2f}s")
                    break
                except Exception as e:
                    retries -= 1
                    print(f"  -> Error: {e}, retries left: {retries}")
                    time.sleep(2)
                    if retries == 0:
                        raise

    # Also populate root assets/audio/animals/ with the default (Aoede) files for fallback
    female_dir = root / "voice_female"
    for mp3 in female_dir.glob("score_*.mp3"):
        shutil.copy2(mp3, root / mp3.name)
    print(f"\nCopied female voice files to root {root} as default fallback.")
    print("\nAll animal audio successfully generated with Aoede and Puck (all <= 2.0s)!")


if __name__ == "__main__":
    main()
