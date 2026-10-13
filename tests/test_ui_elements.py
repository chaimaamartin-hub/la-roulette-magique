from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ui_elements import UIButton, UICheckbox


def test_ui_button_clicks_and_hover() -> None:
    btn = UIButton(rect=pygame.Rect(100, 100, 200, 60), text="Jouer")
    assert btn.is_hovered((150, 120))
    assert not btn.is_hovered((50, 50))

    assert btn.is_clicked((150, 120))
    assert not btn.is_clicked((350, 120))


def test_ui_checkbox_toggle_and_click() -> None:
    box = UICheckbox(rect=pygame.Rect(50, 50, 40, 40), label="A", checked=False)
    assert not box.checked

    assert box.is_clicked((60, 60))
    assert not box.is_clicked((10, 10))

    assert box.toggle()  # now True
    assert box.checked
def test_ui_icon_button() -> None:
    from src.ui_elements import UIIconButton

    btn = UIIconButton(rect=pygame.Rect(50, 50, 80, 80), icon_type="PLAY")
    assert btn.is_hovered((90, 90))
    assert not btn.is_hovered((10, 10))
    assert btn.is_clicked((90, 90))

    surf = pygame.Surface((200, 200))
    btn.render(surf, mouse_pos=(90, 90))


def test_draw_progress_circles() -> None:
    from src.ui_icons import (
        draw_arrow_left_icon,
        draw_close_circle_icon,
        draw_gear_icon,
        draw_play_icon,
        draw_progress_circles,
    )

    surf = pygame.Surface((500, 100))
    # 2 correct, 1 wrong, 7 unplayed
    results = [True, True, False]
    draw_progress_circles(surf, center_pos=(250, 50), round_results=results, total_rounds=10)

    # Test all icon draw functions directly
    draw_play_icon(surf, (50, 50), 30, (0, 0, 0))
    draw_gear_icon(surf, (100, 50), 20, (0, 0, 0))
    draw_close_circle_icon(surf, (150, 50), 20, (0, 0, 0))
    draw_arrow_left_icon(surf, (200, 50), 30, (0, 0, 0))

