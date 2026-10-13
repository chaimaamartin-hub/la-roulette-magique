from pathlib import Path
import random
import sys
from typing import Literal
import pygame

VoiceType = Literal["FEMALE", "MALE"]


SCORE_ANIMAL_AUDIO_MAP: dict[int, str] = {
    0: "score_0_ant.mp3",
    1: "score_1_fly.mp3",
    2: "score_2_frog.mp3",
    3: "score_3_duck.mp3",
    4: "score_4_bunny.mp3",
    5: "score_5_cat.mp3",
    6: "score_6_dog.mp3",
    7: "score_7_fox.mp3",
    8: "score_8_sheep.mp3",
    9: "score_9_lion.mp3",
    10: "score_10_bear.mp3",
}


def get_default_assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            meipass_p = Path(sys._MEIPASS) / "assets" / "audio"
            if meipass_p.is_dir():
                return meipass_p
        exe_p = Path(sys.executable).resolve().parent / "assets" / "audio"
        if exe_p.is_dir():
            return exe_p
    return Path(__file__).resolve().parent.parent / "assets" / "audio"


class AudioManager:
    def __init__(self, assets_dir: Path | None = None) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(8)

        base = assets_dir or get_default_assets_dir()
        self.assets_dir: Path = base
        self.sfx_dir: Path = base / "sfx"
        self.female_voice_dir: Path = base / "voice_female"
        self.male_voice_dir: Path = base / "voice_male"
        self.animals_dir: Path = base / "animals"

        self.current_voice: VoiceType = "FEMALE"

        self.channel_sfx: pygame.mixer.Channel = pygame.mixer.Channel(0)
        self.channel_voice: pygame.mixer.Channel = pygame.mixer.Channel(1)

        self._sfx_correct: pygame.mixer.Sound | None = None
        self._sfx_wrong: pygame.mixer.Sound | None = None
        self._load_sfx()

    def _load_sfx(self) -> None:
        correct_path = self.sfx_dir / "correct.mp3"
        wrong_path = self.sfx_dir / "wrong.wav"

        if correct_path.is_file():
            self._sfx_correct = pygame.mixer.Sound(str(correct_path))
        if wrong_path.is_file():
            self._sfx_wrong = pygame.mixer.Sound(str(wrong_path))

    def set_voice(self, voice: VoiceType) -> None:
        if voice not in ("FEMALE", "MALE"):
            raise ValueError(f"CRITICAL: Unknown voice '{voice}'. Must be 'FEMALE' or 'MALE'.")
        self.current_voice = voice

    def pick_random_voice(self) -> VoiceType:
        chosen: VoiceType = random.choice(["FEMALE", "MALE"])
        self.set_voice(chosen)
        return chosen

    def get_active_voice_dir(self) -> Path:
        return self.female_voice_dir if self.current_voice == "FEMALE" else self.male_voice_dir

    def resolve_audio_path(
        self,
        symbol: str,
        utterance_type: Literal["question", "ans_pos", "ans_neg"],
    ) -> Path:
        if not symbol or not symbol.strip():
            raise ValueError("CRITICAL: Symbol cannot be empty.")

        is_digit = symbol.strip().isdigit()
        cat = "number" if is_digit else "letter"
        # Normalize letters to uppercase for audio file lookup
        normalized_sym = symbol.strip() if is_digit else symbol.strip().upper()

        if utterance_type == "question":
            prefix = "q"
        elif utterance_type == "ans_pos":
            prefix = "ans_pos"
        elif utterance_type == "ans_neg":
            prefix = "ans_neg"
        else:
            raise ValueError(f"CRITICAL: Unknown utterance type '{utterance_type}'.")

        filename = f"{prefix}_{cat}_{normalized_sym}.mp3"
        return self.get_active_voice_dir() / filename

    def play_sfx_correct(self) -> None:
        if self._sfx_correct is not None:
            self.channel_sfx.play(self._sfx_correct)

    def play_sfx_wrong(self) -> None:
        if self._sfx_wrong is not None:
            self.channel_sfx.play(self._sfx_wrong)

    def play_voice(
        self,
        symbol: str,
        utterance_type: Literal["question", "ans_pos", "ans_neg"],
    ) -> bool:
        path = self.resolve_audio_path(symbol, utterance_type)
        if not path.is_file():
            raise FileNotFoundError(f"CRITICAL: Voice file not found at {path}")

        sound = pygame.mixer.Sound(str(path))
        self.channel_voice.play(sound)
        return True

    def is_voice_busy(self) -> bool:
        return self.channel_voice.get_busy()

    def play_animal_sound(self, score: int) -> bool:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")

        filename = SCORE_ANIMAL_AUDIO_MAP[score]
        subfolder = "voice_female" if self.current_voice == "FEMALE" else "voice_male"
        voice_path = self.animals_dir / subfolder / filename
        path = voice_path if voice_path.is_file() else (self.animals_dir / filename)
        if not path.is_file():
            raise FileNotFoundError(f"CRITICAL: Animal sound file not found at {path}")

        sound = pygame.mixer.Sound(str(path))
        self.channel_voice.play(sound)
        return True

    def stop_all(self) -> None:
        self.channel_sfx.stop()
        self.channel_voice.stop()
