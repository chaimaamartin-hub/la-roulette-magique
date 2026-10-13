from pathlib import Path
import sys
from typing import TypedDict
import pygame

SCORE_ANIMAL_MAP: dict[int, str] = {
    0: "score_0_ant.png",
    1: "score_1_fly.png",
    2: "score_2_frog.png",
    3: "score_3_duck.png",
    4: "score_4_bunny.png",
    5: "score_5_cat.png",
    6: "score_6_dog.png",
    7: "score_7_fox.png",
    8: "score_8_sheep.png",
    9: "score_9_lion.png",
    10: "score_10_bear.png",
}


class ScoreMotivation(TypedDict):
    spoken: str
    french: str
    english: str


SCORE_MOTIVATION_MESSAGES: dict[int, ScoreMotivation] = {
    0: {
        "spoken": "Hop, hop ! Courage, réessaie !",
        "french": "Courage, réessaie !",
        "english": "Don't give up, try again!",
    },
    1: {
        "spoken": "Bzz, bzz ! Continue, tu peux le faire !",
        "french": "Continue, tu peux le faire !",
        "english": "Keep going, you can do it!",
    },
    2: {
        "spoken": "Coâ, coâ ! C'est un bon début !",
        "french": "C'est un bon début !",
        "english": "That's a good start!",
    },
    3: {
        "spoken": "Coin, coin ! Tu apprends vite !",
        "french": "Tu apprends vite !",
        "english": "You're learning fast!",
    },
    4: {
        "spoken": "Hop, hop ! Continue comme ça !",
        "french": "Continue comme ça !",
        "english": "Keep it up, you're doing great!",
    },
    5: {
        "spoken": "Miaou, miaou ! C'est super !",
        "french": "C'est super !",
        "english": "That's wonderful!",
    },
    6: {
        "spoken": "Ouaf, ouaf ! Tu y es presque !",
        "french": "Tu y es presque !",
        "english": "You're getting there!",
    },
    7: {
        "spoken": "Yap, yap ! Bien joué, petit malin !",
        "french": "Bien joué, petit malin !",
        "english": "Well played, clever one!",
    },
    8: {
        "spoken": "Bêê, bêê ! Formidable !",
        "french": "Formidable !",
        "english": "Fantastic work!",
    },
    9: {
        "spoken": "Rrroaar ! Très bien !",
        "french": "Très bien !",
        "english": "Very good!",
    },
    10: {
        "spoken": "Grrroaar ! Parfait !",
        "french": "Parfait !",
        "english": "Perfect!",
    },
}


def get_score_subtitle(score: int) -> str:
    if not isinstance(score, int):
        raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
    if score < 0 or score > 10:
        raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
    entry = SCORE_MOTIVATION_MESSAGES[score]
    return f"{entry['french']} - {entry['english']}"


def get_animals_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / "images" / "animals"


def get_animals_videos_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / "videos" / "animals"


class AnimalManager:
    def __init__(
        self,
        animals_dir: Path | None = None,
        videos_dir: Path | None = None,
    ) -> None:
        self.animals_dir: Path = animals_dir if animals_dir is not None else get_animals_dir()
        if not self.animals_dir.is_dir():
            raise FileNotFoundError(f"CRITICAL: Animals directory not found at {self.animals_dir}")
        self.videos_dir: Path = videos_dir if videos_dir is not None else get_animals_videos_dir()
        self._raw_cache: dict[int, pygame.Surface] = {}
        self._scaled_cache: dict[tuple[int, int], pygame.Surface] = {}

    def get_video_path(self, score: int) -> Path | None:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
        if not self.videos_dir.is_dir():
            return None

        img_name = SCORE_ANIMAL_MAP[score]
        stem = Path(img_name).stem
        for ext in (".mp4", ".mov", ".mkv", ".webm"):
            cand = self.videos_dir / f"{stem}{ext}"
            if cand.is_file():
                return cand

        for p in self.videos_dir.glob(f"score_{score}_*"):
            if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"):
                return p

        return None

    def has_video(self, score: int) -> bool:
        return self.get_video_path(score) is not None

    def get_animal_surface(self, score: int, target_size: int) -> pygame.Surface:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
        if target_size <= 0:
            raise ValueError(f"CRITICAL: target_size must be positive, got {target_size}")

        cache_key = (score, target_size)
        if cache_key in self._scaled_cache:
            return self._scaled_cache[cache_key]

        if score not in self._raw_cache:
            filename = SCORE_ANIMAL_MAP[score]
            file_path = self.animals_dir / filename
            if not file_path.is_file():
                raise FileNotFoundError(f"CRITICAL: Animal image not found at {file_path}")
            loaded = pygame.image.load(str(file_path))
            if pygame.display.get_surface() is not None:
                loaded = loaded.convert_alpha()
            self._raw_cache[score] = loaded

        raw_surf = self._raw_cache[score]
        scaled = pygame.transform.smoothscale(raw_surf, (target_size, target_size))
        self._scaled_cache[cache_key] = scaled
        return scaled

    def render_animal(
        self,
        surface: pygame.Surface,
        score: int,
        center_pos: tuple[int, int],
        size: int,
    ) -> None:
        animal_surf = self.get_animal_surface(score, size)
        rect = animal_surf.get_rect(center=center_pos)
        surface.blit(animal_surf, rect)
