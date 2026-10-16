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


def test_config_screen_distinct_case_insensitive_minimum(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import src.menu_screens as ms_mod

    monkeypatch.setattr(ms_mod, "save_config", lambda c: tmp_path / "cfg.json")

    # Pool has 6 checkboxes checked ('A', 'a', 'B', 'C', 'D', 'E'), which is 5 distinct letters
    cfg = GameConfig(selected_symbols=["A", "a", "B", "C", "D", "E"])
    screen = ConfigScreen(1280, 720, cfg)

    # 1 Happy path: Unchecking 'a' is allowed because 'A', 'B', 'C', 'D', 'E' still leaves 5 distinct letters
    box_B = [b for b in screen.checkboxes if b.label == "B"][0]
    box_a = [b for b in screen.checkboxes if b.label == "a"][0]

    # 2 Failure path 1: Trying to uncheck 'B' when only 5 distinct letters exist (even with 6 boxes checked) is blocked
    ev_click_B = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_B.rect.center})
    screen.handle_event(ev_click_B)
    assert box_B.checked
    assert screen.error_message == "Choisis au moins 5 lettres ou chiffres !"

    # Happy path: Unchecking 'a' succeeds because 'A' remains checked (still 5 distinct letters)
    ev_click_a = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_a.rect.center})
    screen.handle_event(ev_click_a)
    assert not box_a.checked

    # 3 Failure path 2: Now unchecking 'A' is blocked because only 4 distinct letters would remain
    box_A = [b for b in screen.checkboxes if b.label == "A"][0]
    ev_click_A = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": box_A.rect.center})
    screen.handle_event(ev_click_A)
    assert box_A.checked



def test_render_title_shimmer_happy_and_failure_paths() -> None:
    from src.menu_screens import render_title_shimmer

    mask = pygame.Surface((200, 50), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    out = render_title_shimmer(mask, anim_t=1.2)
    assert out.get_size() == (200, 50)

    with pytest.raises(ValueError, match="CRITICAL: anim_t must be a valid number"):
        render_title_shimmer(mask, float("nan"))

    empty_mask = pygame.Surface((0, 50), pygame.SRCALPHA)
    with pytest.raises(ValueError, match="CRITICAL: title_mask dimensions must be positive"):
        render_title_shimmer(empty_mask, 1.0)


def test_score_screen_animal_click_replay_happy_path() -> None:
    from unittest.mock import MagicMock
    from src.score_screen import ScoreScreen

    audio_mgr = MagicMock()
    screen = ScoreScreen(1280, 720, score=9, audio_mgr=audio_mgr)
    try:
        # Upon initialization, play_animal_sound was called once
        assert audio_mgr.play_animal_sound.call_count == 1
        audio_mgr.reset_mock()

        # Advance time so fade-in completes and mark animation finished
        screen.anim_time = screen.fade_duration + 0.1
        if screen.video_player is not None:
            screen.video_player.is_finished = True
        else:
            screen.bounce_anim_time = screen.bounce_duration

        assert screen.is_animal_animation_finished() is True

        animal_rect = screen.get_animal_rect()
        ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": animal_rect.center})
        action = screen.handle_event(ev_click)

        # Replay event does not navigate away
        assert action is None
        audio_mgr.play_animal_sound.assert_called_once_with(9)
        assert screen.is_animal_animation_finished() is False
    finally:
        screen.close()


def test_score_screen_animal_click_failure_paths() -> None:
    from unittest.mock import MagicMock
    from src.score_screen import ScoreScreen

    audio_mgr = MagicMock()
    screen = ScoreScreen(1280, 720, score=9, audio_mgr=audio_mgr)
    try:
        # Reset mock call from __init__
        audio_mgr.reset_mock()

        # 1. Failure path 1: Non-tuple/list pos in is_animal_clicked raises TypeError
        with pytest.raises(TypeError, match="CRITICAL: pos must be a tuple"):
            screen.is_animal_clicked("invalid_pos")  # type: ignore[arg-type]

        with pytest.raises(TypeError, match="CRITICAL: pos must be a tuple"):
            screen.is_animal_clicked((100,))  # type: ignore[arg-type]

        # 2. Failure path 2: Clicking before animation finishes does not trigger replay
        screen.anim_time = 0.1
        animal_rect = screen.get_animal_rect()
        ev_early = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": animal_rect.center})
        screen.handle_event(ev_early)
        audio_mgr.play_animal_sound.assert_not_called()

        # 3. Failure path 3: Clicking outside the animal rect returns False and does not trigger replay
        screen.anim_time = screen.fade_duration + 0.1
        if screen.video_player is not None:
            screen.video_player.is_finished = True
        assert screen.is_animal_clicked((0, 0)) is False
        ev_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (0, 0)})
        screen.handle_event(ev_outside)
        audio_mgr.play_animal_sound.assert_not_called()
    finally:
        screen.close()


def test_compute_star_drop_state_happy_and_failure_paths() -> None:
    from src.score_screen import compute_star_drop_state

    # 1. Happy path: Starts at start_y, overshoots with scale pop near landing, settles at 0 offset & 1.0 scale
    off_start, scale_start = compute_star_drop_state(0.0, 0, -80.0, 120.0)
    assert off_start == -200
    assert scale_start == pytest.approx(1.0)

    off_land, scale_land = compute_star_drop_state(0.34, 0, -80.0, 120.0)
    assert off_land > 0  # Elastic overshoot past target_y
    assert scale_land > 1.05  # Landing scale pop

    off_done, scale_done = compute_star_drop_state(1.0, 0, -80.0, 120.0)
    assert off_done == 0
    assert scale_done == pytest.approx(1.0)

    # 2. Failure paths: invalid anim_time and invalid star_index
    with pytest.raises(ValueError, match="CRITICAL: anim_time must be a valid number"):
        compute_star_drop_state(float("nan"), 0, -80.0, 120.0)
    with pytest.raises(ValueError, match="CRITICAL: star_index must be a non-negative integer"):
        compute_star_drop_state(0.2, -1, -80.0, 120.0)
    with pytest.raises(ValueError, match="CRITICAL: star_index must be a non-negative integer"):
        compute_star_drop_state(0.2, True, -80.0, 120.0)  # type: ignore[arg-type]


def test_compute_star_rainbow_wave_happy_and_failure_paths() -> None:
    from src.score_screen import compute_star_rainbow_wave

    # 1. Happy path: Unearned star is None; earned star sweeps 0.0 -> 1.0 then settles to None (gold)
    assert compute_star_rainbow_wave(0.5, 0, False) is None
    p0 = compute_star_rainbow_wave(0.4, 0, True)
    p3 = compute_star_rainbow_wave(0.4, 3, True)
    assert p0 is not None and p3 is not None
    assert 0.0 < p3 < p0 < 1.0  # Left-to-right staggered wave
    assert compute_star_rainbow_wave(2.0, 0, True) is None  # Settled on gold

    # 2. Failure paths: invalid anim_time, negative star_index, non-bool is_earned
    with pytest.raises(ValueError, match="CRITICAL: anim_time must be a valid number"):
        compute_star_rainbow_wave(float("nan"), 0, True)
    with pytest.raises(ValueError, match="CRITICAL: star_index must be a non-negative integer"):
        compute_star_rainbow_wave(0.3, -2, True)
    with pytest.raises(TypeError, match="CRITICAL: is_earned must be a boolean"):
        compute_star_rainbow_wave(0.3, 0, 1)  # type: ignore[arg-type]


def test_compute_animal_entrance_scale_happy_and_failure_paths() -> None:
    from src.score_screen import compute_animal_entrance_scale

    # 1. Happy path: Starts at 0.86, overshoots > 1.0, settles at 1.0
    assert compute_animal_entrance_scale(0.0, 0.45) == pytest.approx(0.86)
    assert compute_animal_entrance_scale(0.30, 0.45) > 1.0
    assert compute_animal_entrance_scale(0.45, 0.45) == pytest.approx(1.0)
    assert compute_animal_entrance_scale(1.0, 0.45) == pytest.approx(1.0)

    # 2. Failure paths: NaN anim_time or non-positive fade_duration
    with pytest.raises(ValueError, match="CRITICAL: anim_time must be a valid number"):
        compute_animal_entrance_scale(float("nan"), 0.45)
    with pytest.raises(ValueError, match="CRITICAL: fade_duration must be a positive number"):
        compute_animal_entrance_scale(0.2, 0.0)
    with pytest.raises(ValueError, match="CRITICAL: fade_duration must be a positive number"):
        compute_animal_entrance_scale(0.2, -0.5)


def test_score_screen_animal_static_hover_and_hidden_click_replay() -> None:
    from unittest.mock import MagicMock
    from src.font_manager import FontManager
    from src.score_screen import ScoreScreen, compute_animal_entrance_scale

    audio_mgr = MagicMock()
    screen = ScoreScreen(1280, 720, score=9, round_results=[True] * 9 + [False], audio_mgr=audio_mgr)
    try:
        audio_mgr.reset_mock()
        surf = pygame.Surface((1280, 720))
        fm = FontManager()

        # 1. Animal entrance settles at 1.0 (no idle pulse, no hover boost)
        screen.anim_time = 1.0
        if screen.video_player is not None:
            screen.video_player.is_finished = True
        assert compute_animal_entrance_scale(screen.anim_time, screen.fade_duration) == 1.0

        # Hovering over animal center produces no scaling or error
        animal_center = screen.get_animal_rect().center
        screen.render(surf, fm, mouse_pos=animal_center)
        screen.update(0.1)

        # 2. Hidden feature: Clicking the finished animal replays video/animation and sound
        ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": animal_center})
        action = screen.handle_event(ev_click)
        assert action is None
        audio_mgr.play_animal_sound.assert_called_once_with(9)
    finally:
        screen.close()



