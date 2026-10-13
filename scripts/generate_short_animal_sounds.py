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
        "text": "Tchiki !",
        "style": "Short, tiny, quick playful squeak of an ant. Very brief, strictly under 1 second.",
    },
    {
        "score": 1,
        "name": "fly",
        "text": "Bzzz !",
        "style": "Short, quick, friendly buzz sound of a fly. Very brief, strictly under 1 second.",
    },
    {
        "score": 2,
        "name": "frog",
        "text": "Coâ, coâ !",
        "style": "Short, cute, friendly double croak of a little frog. Quick, under 1.2 seconds.",
    },
    {
        "score": 3,
        "name": "duck",
        "text": "Coin, coin !",
        "style": "Short, cheerful double quack of a little duck. Quick, under 1.2 seconds.",
    },
    {
        "score": 4,
        "name": "bunny",
        "text": "Hop !",
        "style": "Short, cute, playful little bunny hop sound. Very brief, strictly under 1 second.",
    },
    {
        "score": 5,
        "name": "cat",
        "text": "Miaou !",
        "style": "Short, gentle, sweet single meow of a cute kitten. Quick, under 1.2 seconds.",
    },
    {
        "score": 6,
        "name": "dog",
        "text": "Ouaf, ouaf !",
        "style": "Short, cheerful, energetic double bark of a puppy. Quick, under 1.2 seconds.",
    },
    {
        "score": 7,
        "name": "fox",
        "text": "Yap, yap !",
        "style": "Short, playful double yip of a clever little fox. Quick, under 1.2 seconds.",
    },
    {
        "score": 8,
        "name": "sheep",
        "text": "Bêêê !",
        "style": "Short, warm, friendly single bleat of a fluffy sheep. Quick, under 1.3 seconds.",
    },
    {
        "score": 9,
        "name": "lion",
        "text": "Roarrr !",
        "style": "Short, playful, cute little roar of a baby lion cub. Quick, under 1.3 seconds.",
    },
    {
        "score": 10,
        "name": "bear",
        "text": "Grrr, roarr !",
        "style": "Short, friendly, rumbling bear roar and growl. Brief, strictly under 1.6 seconds.",
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
    # Convert to MP3 and strictly limit duration to max_duration with gentle fade out at end
    fade_start = max(0.5, max_duration - 0.25)
    filter_arg = f"atrim=0:{max_duration},afade=t=out:st={fade_start}:d=0.25"
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
                        max_duration=1.85,
                    )
                    dur = get_duration(out_file)
                    print(f"  -> Saved {out_file.name}: duration = {dur:.2f}s (<= 2.0s OK)")
                    assert dur <= 2.0, f"Duration {dur} exceeds 2.0s"
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
