from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import GameConfig
from src.menu_screens import ConfigScreen, MainMenuScreen, ScoreScreen


def test_main_menu_button_clicks() -> None:
    menu = MainMenuScreen(1280, 720)

    # Vertical alignment check
    assert menu.btn_play.rect.centerx == menu.btn_config.rect.centerx == menu.btn_quit.rect.centerx
    assert menu.btn_play.rect.centery < menu.btn_config.rect.centery < menu.btn_quit.rect.centery

    # Click Play
    event_play = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.btn_play.rect.center})
    assert menu.handle_event(event_play) == "PLAY"

    # Click Config
    event_cfg = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.btn_config.rect.center})
    assert menu.handle_event(event_cfg) == "CONFIG"

    # Click Quit
    event_quit = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.btn_quit.rect.center})
    assert menu.handle_event(event_quit) == "QUIT"

    # Click outside
    event_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})
    assert menu.handle_event(event_outside) is None


def test_config_screen_back_and_autosave() -> None:
    cfg = GameConfig(selected_symbols=["A", "B", "C", "D", "E", "F"])
    screen = ConfigScreen(1280, 720, cfg)

    # Click Back
    ev_back = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_back.rect.center})
    assert screen.handle_event(ev_back) == "MENU"

    # Find checkbox for 'F' (currently checked, total 6)
    box_f = [b for b in screen.checkboxes if b.label == "F"][0]
    ev_f = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_f.rect.center})
    screen.handle_event(ev_f)
    assert not box_f.checked
    # Autosaved to cfg
    assert "F" not in cfg.selected_symbols
    assert len(cfg.selected_symbols) == 5

    # Now total is 5; trying to uncheck 'E' must be prevented to maintain >= 5
    box_e = [b for b in screen.checkboxes if b.label == "E"][0]
    ev_e = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_e.rect.center})
    screen.handle_event(ev_e)
    assert box_e.checked
    assert "E" in cfg.selected_symbols
    assert len(cfg.selected_symbols) == 5


def test_score_screen_buttons_and_render() -> None:
    from src.font_manager import FontManager

    score = ScoreScreen(1280, 720, score=10, max_score=10)
    ev_replay = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": score.btn_replay.rect.center})
    assert score.handle_event(ev_replay) == "PLAY"

    ev_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (10, 10)})
    assert score.handle_event(ev_outside) is None

    # Render check
    surf = pygame.Surface((1280, 720))
    fm = FontManager()
    score.render(surf, fm, mouse_pos=(100, 100))

