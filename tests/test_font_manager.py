from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.font_manager import FontManager, WINDOWS_FONTS


@pytest.fixture(scope="module", autouse=True)
def init_pygame_font() -> None:
    if not pygame.font.get_init():
        pygame.font.init()


def test_font_manager_get_font_and_caching() -> None:
    fm = FontManager()
    font1 = fm.get_font("Segoe UI", 32, bold=True)
    assert font1 is not None
    font2 = fm.get_font("Segoe UI", 32, bold=True)
    # Caching returns exact same font instance
    assert font1 is font2


def test_font_manager_variety_cycling() -> None:
    fm = FontManager(["FontA", "FontB"])
    f0 = fm.get_card_font(0, 48)
    f1 = fm.get_card_font(1, 48)
    f2 = fm.get_card_font(2, 48)
    assert f0 is not None and f1 is not None
    # Index 2 wraps back to index 0
    assert f2 is f0


def test_font_manager_invalid_size() -> None:
    fm = FontManager()
    with pytest.raises(ValueError, match="CRITICAL: Font size must be positive"):
        fm.get_font("Segoe UI", 0)

    with pytest.raises(ValueError, match="CRITICAL: Font size must be positive"):
        fm.get_font("Segoe UI", -10)


def test_get_title_font() -> None:
    fm = FontManager()

    # Happy path: Returns a valid pygame Font instance
    title_font = fm.get_title_font(48)
    assert isinstance(title_font, pygame.font.Font)

    # Failure path 1: Non-positive size (0) raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: Font size must be positive"):
        fm.get_title_font(0)

    # Failure path 2: Negative size (-12) raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: Font size must be positive"):
        fm.get_title_font(-12)

