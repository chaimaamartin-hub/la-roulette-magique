from pathlib import Path
import sys
import time
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

    # Render check
    from src.font_manager import FontManager
    surf = pygame.Surface((1280, 720))
    fm = FontManager()
    menu.render(surf, fm, mouse_pos=(100, 100))
    # Verify title font at 1080p produces expected ~77pt size
    title_font = fm.get_title_font(int(77 * 1.0))
    assert title_font.get_height() > 60



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

    # Test animation updates
    score.update(0.2)
    score.render(surf, fm, mouse_pos=(100, 100))
    score.update(0.4)
    score.render(surf, fm, mouse_pos=(100, 100))


def test_score_screen_validation_failure_paths() -> None:
    # Failure path: Invalid screen dimensions
    with pytest.raises(ValueError, match="CRITICAL: screen dimensions must be positive"):
        ScoreScreen(0, 720, score=5)
    with pytest.raises(ValueError, match="CRITICAL: screen dimensions must be positive"):
        ScoreScreen(1280, -100, score=5)


def test_config_screen_prompt_modes_toggles_and_constraints() -> None:
    from src.font_manager import FontManager

    cfg = GameConfig(
        selected_symbols=["A", "B", "C", "D", "E"],
        ask_letter_names=True,
        ask_letter_sounds=False,
    )
    screen = ConfigScreen(1280, 720, cfg)

    # Initially: names=True, sounds=False
    assert screen.btn_mode_names.checked
    assert not screen.btn_mode_sounds.checked

    # Failure path 1: Cannot uncheck names when sounds is False
    ev_names = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_mode_names.rect.center}
    )
    screen.handle_event(ev_names)
    assert screen.btn_mode_names.checked
    assert cfg.ask_letter_names

    # Happy path: Check sounds -> both active
    ev_sounds = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_mode_sounds.rect.center}
    )
    screen.handle_event(ev_sounds)
    assert screen.btn_mode_sounds.checked
    assert cfg.ask_letter_sounds

    # Now uncheck names -> only sounds active
    screen.handle_event(ev_names)
    assert not screen.btn_mode_names.checked
    assert not cfg.ask_letter_names
    assert screen.btn_mode_sounds.checked

    # Failure path 2: Cannot uncheck sounds when names is False
    screen.handle_event(ev_sounds)
    assert screen.btn_mode_sounds.checked
    assert cfg.ask_letter_sounds

    # Render check
    surf = pygame.Surface((1280, 720))
    fm = FontManager()
    screen.render(surf, fm, mouse_pos=(100, 100))


def test_config_screen_error_message_text() -> None:
    from src.font_manager import FontManager

    cfg = GameConfig(
        selected_symbols=["A", "B", "C", "D", "E"],
        ask_letter_names=True,
        ask_letter_sounds=False,
    )
    screen = ConfigScreen(1280, 720, cfg)

    # 1. Happy path: Initially no error message
    assert screen.error_message == ""
    assert screen.error_hide_time == 0.0

    # 2. Failure path 1: Deselecting below 5 triggers error message
    box_a = [b for b in screen.checkboxes if b.label == "A"][0]
    ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_a.rect.center})
    screen.handle_event(ev_click)
    assert screen.error_message == "Choisis au moins 5 lettres ou chiffres !"
    assert screen.error_hide_time > time.time()
    assert box_a.checked  # Remains checked

    # 3. Failure path 2: Unchecking single active prompt mode triggers error message
    ev_mode = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_mode_names.rect.center})
    screen.handle_event(ev_mode)
    assert screen.error_message == "Choisis au moins un mode de jeu !"
    assert screen.error_hide_time > time.time()
    assert screen.btn_mode_names.checked

    # 4. Render check: Error message text renders onto surface cleanly
    surf = pygame.Surface((1280, 720))
    fm = FontManager()
    screen.render(surf, fm, mouse_pos=(100, 100))




