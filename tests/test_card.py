from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.card import Card, ease_out_cubic


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


