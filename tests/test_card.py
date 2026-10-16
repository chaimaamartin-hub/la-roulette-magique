from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.card import Card, RAINBOW_12_HUES, ease_out_cubic, sample_rainbow_band_color


def test_ease_out_cubic_bounds() -> None:
    assert ease_out_cubic(0.0) == 0.0
    assert ease_out_cubic(1.0) == 1.0
    assert ease_out_cubic(-0.5) == 0.0
    assert ease_out_cubic(1.5) == 1.0
    assert ease_out_cubic(0.5) > 0.5  # deceleration curve


def test_card_fly_in_progression() -> None:
    target_rect = pygame.Rect(400, 300, 200, 280)
    card = Card(symbol="A", index=0, target_rect=target_rect, screen_width=1280)

    assert card.state == "FLYING_IN"
    assert card.current_x < 0

    # Halfway through fly-in
    card.update(0.25)
    assert card.state == "FLYING_IN"
    assert card.current_x > -200

    # Finish fly-in
    card.update(0.35)
    assert card.state == "IDLE"
    assert card.current_x == 400.0


def test_card_hit_testing() -> None:
    target_rect = pygame.Rect(400, 300, 200, 280)
    card = Card(symbol="A", index=0, target_rect=target_rect, screen_width=1280)

    # Cannot click while flying in
    assert not card.is_clicked((450, 350))

    # Finish fly-in
    card.update(1.0)
    assert card.state == "IDLE"

    # Click inside
    assert card.is_clicked((450, 350))
    # Click outside
    assert not card.is_clicked((100, 100))


def test_card_triggers_and_effects() -> None:
    target_rect = pygame.Rect(400, 300, 200, 280)
    card = Card(symbol="B", index=1, target_rect=target_rect, screen_width=1280)
    card.update(1.0)

    card.trigger_rainbow()
    assert card.state == "RAINBOW_FLASH"
    card.update(card.rainbow_duration + 0.1)
    assert card.state == "IDLE"

    card.trigger_red_flash()
    assert card.state == "RED_FLASH"
    assert card.is_wrong is True
    card.update(card.red_flash_duration + 0.1)
    assert card.state == "IDLE"
    assert card.is_wrong is True


def test_card_hover_render() -> None:
    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="C", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)  # Move to IDLE
    assert card.state == "IDLE"

    font = pygame.font.SysFont("arial", 32)
    surf = pygame.Surface((800, 600))

    # Render without hover -> white background
    card.render(surf, font, mouse_pos=(10, 10))
    # Render with hover -> very light yellow background (255, 252, 220)
    card.render(surf, font, mouse_pos=(150, 150))
    # Pixel inside card should be light yellow
    pixel = surf.get_at((150, 150))
    assert (pixel.r, pixel.g, pixel.b) == (255, 252, 220)


def test_card_wrong_grayed_out_happy_path() -> None:
    # 1 Happy Path: wrong card flashes then settles into grayed-out state and ignores hover
    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="D", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)  # Move to IDLE
    assert not card.is_wrong

    card.trigger_red_flash()
    assert card.is_wrong
    card.update(card.red_flash_duration + 0.1)

    # State returns to IDLE but is_wrong remains True
    assert card.state == "IDLE"
    assert card.is_wrong

    font = pygame.font.SysFont("arial", 32)
    surf = pygame.Surface((800, 600))

    # Render while hovering over wrong card: should remain gray (235, 235, 238), NOT yellow
    card.render(surf, font, mouse_pos=(150, 150))
    pixel = surf.get_at((150, 150))
    assert (pixel.r, pixel.g, pixel.b) == (235, 235, 238)


def test_card_wrong_click_disabled_failure_path() -> None:
    # 2 Failure Path A: clicks on a wrong card are rejected
    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="E", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    assert card.is_clicked((150, 150))

    card.trigger_red_flash()
    # While flashing or once marked wrong, clicks inside are rejected
    assert not card.is_clicked((150, 150))

    card.update(card.red_flash_duration + 0.1)
    # After flash completes, clicks inside remain rejected
    assert not card.is_clicked((150, 150))


def test_card_wrong_click_out_of_bounds_failure_path() -> None:
    # 2 Failure Path B: clicks outside wrong card are rejected
    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="F", index=0, target_rect=target_rect, screen_width=800)
    card.trigger_red_flash()
    assert not card.is_clicked((0, 0))
    assert not card.is_clicked((-50, -50))


def test_card_hover_raise_and_click_happy_path() -> None:
    # Happy path: Card elevation on hover and successful click in the raised upper bounds
    target_rect = pygame.Rect(200, 200, 130, 180)
    card = Card(symbol="G", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    assert card.state == "IDLE"

    raise_amount = max(5, min(10, card.height // 26))
    # Point located in the raised top sliver (above standard rect.y, within rect.y - raise_amount)
    raised_point = (250, target_rect.y - raise_amount + 1)
    assert card.is_clicked(raised_point)

    font = pygame.font.SysFont("arial", 32)
    surf = pygame.Surface((800, 600))
    # Render with mouse at raised point -> should be rendered elevated
    card.render(surf, font, mouse_pos=raised_point)


def test_card_click_above_raised_bounds_failure_path() -> None:
    # Failure path 1: Click strictly above the raised bounds is rejected
    target_rect = pygame.Rect(200, 200, 130, 180)
    card = Card(symbol="H", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)

    raise_amount = max(5, min(10, card.height // 26))
    too_high_point = (250, target_rect.y - raise_amount - 5)
    assert not card.is_clicked(too_high_point)


def test_card_hover_disabled_when_wrong_failure_path() -> None:
    # Failure path 2: When marked wrong, click in raised bounds is rejected
    target_rect = pygame.Rect(200, 200, 130, 180)
    card = Card(symbol="I", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    card.trigger_red_flash()
    card.update(card.red_flash_duration + 0.1)
    assert card.is_wrong

    raise_amount = max(5, min(10, card.height // 26))
    raised_point = (250, target_rect.y - raise_amount + 1)
    assert not card.is_clicked(raised_point)


def test_card_correct_enlargement_happy_path() -> None:
    # 1 Happy Path: Correct card triggers rainbow, marks is_correct, and scales up by ~10%
    target_rect = pygame.Rect(300, 200, 160, 220)
    card = Card(symbol="J", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    assert card.state == "IDLE"
    assert card.is_correct is False

    card.trigger_rainbow()
    assert card.is_correct is True
    assert card.state == "RAINBOW_FLASH"

    # Advance time through pop-up animation
    card.update(0.15)

    surf = pygame.Surface((800, 600))
    surf.fill((0, 0, 0))
    font = pygame.font.SysFont("segoeui", 32)
    card.render(surf, font)

    # 10% enlargement on width 160 means +16px (8px on each side)
    # Point at target_rect.x - 4 is outside normal card, but inside enlarged card
    pixel_left = surf.get_at((target_rect.x - 4, target_rect.centery))
    assert (pixel_left.r, pixel_left.g, pixel_left.b) != (0, 0, 0)

    # Point at target_rect.right + 4 is also inside enlarged card
    pixel_right = surf.get_at((target_rect.right + 3, target_rect.centery))
    assert (pixel_right.r, pixel_right.g, pixel_right.b) != (0, 0, 0)


def test_card_normal_idle_not_enlarged_failure_path() -> None:
    # 2 Failure Path 1: Idle unselected card does not enlarge (is_correct is False)
    target_rect = pygame.Rect(300, 200, 160, 220)
    card = Card(symbol="K", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    assert card.is_correct is False

    surf = pygame.Surface((800, 600))
    surf.fill((0, 0, 0))
    font = pygame.font.SysFont("segoeui", 32)
    card.render(surf, font)

    # Far outside normal card (outside drop shadow margin)
    pixel_outside = surf.get_at((target_rect.x - 20, target_rect.centery))
    assert (pixel_outside.r, pixel_outside.g, pixel_outside.b) == (0, 0, 0)


def test_card_wrong_red_flash_not_enlarged_failure_path() -> None:
    # 2 Failure Path 2: Card with wrong guess does not set is_correct and does not enlarge
    target_rect = pygame.Rect(300, 200, 160, 220)
    card = Card(symbol="L", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    card.trigger_red_flash()
    assert card.is_wrong is True
    assert card.is_correct is False

    card.update(0.15)
    surf = pygame.Surface((800, 600))
    surf.fill((0, 0, 0))
    font = pygame.font.SysFont("segoeui", 32)
    card.render(surf, font)

    pixel_outside = surf.get_at((target_rect.x - 20, target_rect.centery))
    assert (pixel_outside.r, pixel_outside.g, pixel_outside.b) == (0, 0, 0)


def test_card_correct_celebration_pastel_animation() -> None:
    target_rect = pygame.Rect(200, 200, 160, 220)
    card = Card(symbol="M", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    assert not card.is_correct

    card.trigger_rainbow()
    assert card.is_correct
    assert card.state == "RAINBOW_FLASH"
    assert card.correct_anim_time == 0.0

    surf = pygame.Surface((800, 600))
    font = pygame.font.SysFont("segoeui", 32)

    # 1. During rainbow flash: Background should have pastel tint (not plain white 255, 255, 255)
    card.update(0.3)
    card.render(surf, font)
    bg_pixel = surf.get_at((target_rect.centerx, target_rect.y + 20))
    # Pastel background is not plain white
    assert (bg_pixel.r, bg_pixel.g, bg_pixel.b) != (255, 255, 255)

    # 2. After rainbow flash finishes (state returns to IDLE while is_correct remains True):
    card.update(card.rainbow_duration + 0.1)
    assert card.state == "IDLE"
    assert card.is_correct
    assert card.correct_anim_time > 0.8

    # Background must STILL have a subtle pastel celebration tint, not pure white
    surf.fill((0, 0, 0))
    card.render(surf, font)
    bg_pixel_idle = surf.get_at((target_rect.centerx, target_rect.y + 20))
    assert (bg_pixel_idle.r, bg_pixel_idle.g, bg_pixel_idle.b) != (255, 255, 255)
    assert (bg_pixel_idle.r, bg_pixel_idle.g, bg_pixel_idle.b) != (0, 0, 0)


def test_diagonal_rainbow_bands_happy_path() -> None:
    assert len(RAINBOW_12_HUES) == 12

    # Different band positions produce distinct rainbow colors
    col_band_0 = sample_rainbow_band_color(0.1, 0.90, 0.95, 0.35)
    col_band_4 = sample_rainbow_band_color(4.1, 0.90, 0.95, 0.35)
    assert col_band_0 != col_band_4

    # Feathered zone smoothly interpolates between band 0 and band 1
    col_start = sample_rainbow_band_color(0.5, 0.90, 0.95, 0.35)
    col_blend = sample_rainbow_band_color(0.85, 0.90, 0.95, 0.35)
    col_next = sample_rainbow_band_color(1.1, 0.90, 0.95, 0.35)
    assert col_blend != col_start
    assert col_blend != col_next

    # Render card with diagonal bands and verify multiple distinct diagonal bands appear on background
    target_rect = pygame.Rect(100, 100, 210, 290)
    card = Card(symbol="A", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    card.trigger_rainbow()
    card.update(0.2)

    surf = pygame.Surface((800, 600))
    surf.fill((255, 255, 255))
    font = pygame.font.SysFont("segoeui", 90, bold=True)
    card.render(surf, font)

    # Sample top-left interior and bottom-right interior (different diagonal bands)
    px_tl = surf.get_at((target_rect.x + 30, target_rect.y + 30))
    px_br = surf.get_at((target_rect.right - 30, target_rect.bottom - 30))
    assert (px_tl.r, px_tl.g, px_tl.b) != (px_br.r, px_br.g, px_br.b)
    # 10% opacity over white ensures background channels remain >= 220 (light tint)
    assert min(px_tl.r, px_tl.g, px_tl.b) >= 220


def test_sample_rainbow_band_color_invalid_params_failure_path() -> None:
    with pytest.raises(ValueError, match="CRITICAL: band_pos"):
        sample_rainbow_band_color(float("nan"), 0.9, 0.9, 0.35)
    with pytest.raises(ValueError, match="CRITICAL: saturation and value"):
        sample_rainbow_band_color(1.0, 1.5, 0.9, 0.35)
    with pytest.raises(ValueError, match="CRITICAL: feather"):
        sample_rainbow_band_color(1.0, 0.9, 0.9, 1.0)


def test_render_rainbow_card_invalid_rect_failure_path() -> None:
    target_rect = pygame.Rect(100, 100, 200, 280)
    card = Card(symbol="Z", index=0, target_rect=target_rect, screen_width=800)
    surf = pygame.Surface((400, 400))
    text_surf = pygame.Surface((20, 20), pygame.SRCALPHA)

    with pytest.raises(ValueError, match="CRITICAL: draw_rect dimensions"):
        card._render_rainbow_card(surf, pygame.Rect(10, 10, 0, 100), 12, text_surf, (10, 10))


def test_card_shake_and_smooth_hover_happy_path() -> None:
    from src.card import compute_shake_offset

    assert compute_shake_offset(0.05, 0.4) != 0
    assert compute_shake_offset(0.4, 0.4) == 0

    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="S", index=0, target_rect=target_rect, screen_width=800)
    card.update(1.0)
    surf = pygame.Surface((800, 600))
    font = pygame.font.SysFont("segoeui", 32)

    card.render(surf, font, mouse_pos=(150, 150))
    first_prog = card.hover_progress
    assert 0.0 < first_prog < 1.0
    card.render(surf, font, mouse_pos=(150, 150))
    assert card.hover_progress > first_prog


def test_compute_shake_offset_failure_paths() -> None:
    from src.card import compute_shake_offset

    with pytest.raises(ValueError, match="CRITICAL: duration must be positive"):
        compute_shake_offset(0.1, 0.0)
    with pytest.raises(ValueError, match="CRITICAL: state_time must be non-negative"):
        compute_shake_offset(-0.1, 0.4)


def test_card_no_hover_while_flying_in() -> None:
    target_rect = pygame.Rect(100, 100, 120, 160)
    card = Card(symbol="A", index=0, target_rect=target_rect, screen_width=800)
    card.update(0.25)
    assert card.state == "FLYING_IN"

    curr_rect = card.get_current_rect()
    surf = pygame.Surface((800, 600))
    font = pygame.font.SysFont("segoeui", 32)

    # Hovering directly over card while FLYING_IN must NOT increase hover_progress or tint yellow
    card.render(surf, font, mouse_pos=curr_rect.center)
    assert card.hover_progress == 0.0

