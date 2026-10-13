from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.animal_manager import AnimalManager


@pytest.fixture(scope="module", autouse=True)
def init_pygame() -> None:
    if not pygame.get_init():
        pygame.init()


def test_animal_manager_happy_path() -> None:
    am = AnimalManager()

    # Load all 11 animals (scores 0 through 10)
    for score in range(11):
        surf = am.get_animal_surface(score, target_size=200)
        assert isinstance(surf, pygame.Surface)
        assert surf.get_size() == (200, 200)

    # Render on surface
    target_surf = pygame.Surface((400, 400))
    am.render_animal(target_surf, score=10, center_pos=(200, 200), size=200)


def test_animal_manager_invalid_score_failure_paths() -> None:
    am = AnimalManager()

    # Failure Path 1: Negative score
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        am.get_animal_surface(-1, target_size=200)

    # Failure Path 2: Score > 10
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        am.get_animal_surface(11, target_size=200)

    # Failure Path 3: Wrong score type
    with pytest.raises(TypeError, match="CRITICAL: score must be an int"):
        am.get_animal_surface("5", target_size=200)  # type: ignore[arg-type]


def test_animal_manager_invalid_size_and_missing_dir_failure_paths(tmp_path: Path) -> None:
    am = AnimalManager()

    # Failure Path: Invalid target_size <= 0
    with pytest.raises(ValueError, match="CRITICAL: target_size must be positive"):
        am.get_animal_surface(0, target_size=0)

    # Failure Path: Missing animals directory
    empty_dir = tmp_path / "non_existent_animals"
    with pytest.raises(FileNotFoundError, match="CRITICAL: Animals directory not found"):
        AnimalManager(animals_dir=empty_dir)


def test_get_score_subtitle() -> None:
    from src.animal_manager import get_score_subtitle

    # Happy path: Returns valid French - English subtitle string
    assert get_score_subtitle(1) == "Continue, tu peux le faire ! - Keep going, you can do it!"
    assert get_score_subtitle(10) == "Parfait ! - Perfect!"
    assert get_score_subtitle(0) == "Courage, réessaie ! - Don't give up, try again!"

    # Failure path 1: Score < 0 raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        get_score_subtitle(-1)

    # Failure path 2: Score > 10 raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        get_score_subtitle(11)

    # Failure path 3: Non-integer score raises TypeError
    with pytest.raises(TypeError, match="CRITICAL: score must be an int"):
        get_score_subtitle(3.5)  # type: ignore[arg-type]

