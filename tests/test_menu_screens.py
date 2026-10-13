from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import GameConfig
from src.menu_screens import ConfigScreen, MainMenuScreen, ScoreScreen


def test_main_menu_button_clicks() -> None:
    menu = MainMenuScreen(1280, 720)

    # Click Play
    event_play = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.btn_play.rect.center})
    assert menu.handle_event(event_play) == "PLAY"

    # Click Config
    event_cfg = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.btn_config.rect.center})
    assert menu.handle_event(event_cfg) == "CONFIG"

    # Click outside
    event_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})
    assert menu.handle_event(event_outside) is None


def test_config_screen_back_and_validation() -> None:
    cfg = GameConfig(selected_symbols=["A", "B", "C", "D", "E"])
    screen = ConfigScreen(1280, 720, cfg)

    # Click Back
    ev_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_back.rect.center})
    assert screen.handle_event(ev_back) == "MENU"

    # Uncheck so count < 5
    for box in screen.checkboxes[:2]:
        box.checked = False

    # Try to save with only 3 checked -> should block and set error_msg
    ev_save = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_save.rect.center})
    res = screen.handle_event(ev_save)
    assert res is None
    assert screen.error_msg is not None
    assert "au moins 5" in screen.error_msg


def test_score_screen_buttons() -> None:
    score = ScoreScreen(1280, 720, score=9, max_score=10)
    ev_replay = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": score.btn_replay.rect.center})
    assert score.handle_event(ev_replay) == "PLAY"

    ev_home = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": score.btn_home.rect.center})
    assert score.handle_event(ev_home) == "MENU"
