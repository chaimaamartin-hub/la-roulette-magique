from pathlib import Path
import sys
import pygame

SCORE_ANIMAL_MAP: dict[int, str] = {
    0: "score_0_fly.svg",
    1: "score_1_bunny.svg",
    2: "score_2_frog.svg",
    3: "score_3_duck.svg",
    4: "score_4_cat.svg",
    5: "score_5_dog.svg",
    6: "score_6_fox.svg",
    7: "score_7_sheep.svg",
    8: "score_8_horse.svg",
    9: "score_9_lion.svg",
    10: "score_10_bear.svg",
}


def get_animals_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / "images" / "animals"


class AnimalManager:
    def __init__(self, animals_dir: Path | None = None) -> None:
        self.animals_dir: Path = animals_dir if animals_dir is not None else get_animals_dir()
        if not self.animals_dir.is_dir():
            raise FileNotFoundError(f"CRITICAL: Animals directory not found at {self.animals_dir}")
        self._cache: dict[tuple[int, int], pygame.Surface] = {}

    def get_animal_surface(self, score: int, target_size: int) -> pygame.Surface:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
        if target_size <= 0:
            raise ValueError(f"CRITICAL: target_size must be positive, got {target_size}")

        cache_key = (score, target_size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        filename = SCORE_ANIMAL_MAP[score]
        file_path = self.animals_dir / filename
        if not file_path.is_file():
            raise FileNotFoundError(f"CRITICAL: Animal SVG not found at {file_path}")

        surf = pygame.image.load_sized_svg(str(file_path), (target_size, target_size))
        self._cache[cache_key] = surf
        return surf

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
