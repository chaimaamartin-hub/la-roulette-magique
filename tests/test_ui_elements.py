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
        draw_progress_stars,
    )

    surf = pygame.Surface((500, 100))
    # 2 correct, 1 wrong, 7 unplayed
    results = [True, True, False]
    draw_progress_circles(surf, center_pos=(250, 50), round_results=results, total_rounds=10)
    draw_progress_stars(
        surf,
        center_pos=(250, 50),
        round_results=results,
        total_rounds=10,
        filled_color=(235, 165, 0),
    )

    # Test all icon draw functions directly
    draw_play_icon(surf, (50, 50), 30, (0, 0, 0))
    draw_gear_icon(surf, (100, 50), 20, (0, 0, 0))
    draw_close_circle_icon(surf, (150, 50), 20, (0, 0, 0))
    draw_arrow_left_icon(surf, (200, 50), 30, (0, 0, 0))


def test_ui_icons_validation_failure_paths() -> None:
    from src.ui_icons import get_symbol_font, render_unicode_symbol

    # Failure Path 1: Invalid font size <= 0
    with pytest.raises(ValueError, match="CRITICAL: Font size must be greater than 0"):
        get_symbol_font(0)
    with pytest.raises(ValueError, match="CRITICAL: Font size must be greater than 0"):
        get_symbol_font(-10)

    # Failure Path 2: Empty symbol string
    surf = pygame.Surface((100, 100))
    with pytest.raises(ValueError, match="CRITICAL: Symbol must not be empty"):
        render_unicode_symbol(surf, (50, 50), "", 24, (0, 0, 0))


def test_get_gear_surface() -> None:
    from unittest.mock import patch
    from src.ui_icons import get_gear_surface

    # Happy path: Returns valid surface with specified dimensions and circular aspect ratio
    gear = get_gear_surface(32, (100, 100, 100))
    assert isinstance(gear, pygame.Surface)
    assert gear.get_size() == (32, 32)
    bounding = gear.get_bounding_rect()
    assert bounding.width == bounding.height, f"Gear is not circular: {bounding.width}x{bounding.height}"

    # Failure path 1: Non-positive size raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: Gear size must be positive"):
        get_gear_surface(0, (255, 255, 255))
    with pytest.raises(ValueError, match="CRITICAL: Gear size must be positive"):
        get_gear_surface(-16, (255, 255, 255))

    # Failure path 2: Missing SVG file raises FileNotFoundError
    with patch("src.ui_icons.get_gear_svg_path", return_value=Path("non_existent_gear.svg")):
        with pytest.raises(FileNotFoundError, match="CRITICAL: Gear SVG not found"):
            get_gear_surface(999, (0, 0, 0))


def test_get_icon_surface_and_bold_icons() -> None:
    from unittest.mock import patch
    from src.ui_icons import (
        draw_arrow_left_icon,
        draw_close_circle_icon,
        draw_gear_icon,
        get_icon_surface,
    )

    # Happy path: Loads bold arrow and close icons
    arr = get_icon_surface("arrow_left", 32, (20, 20, 25))
    assert isinstance(arr, pygame.Surface)
    assert arr.get_size() == (32, 32)

    close_icon = get_icon_surface("close", 32, (20, 20, 25))
    assert isinstance(close_icon, pygame.Surface)
    assert close_icon.get_size() == (32, 32)

    # Rendering on canvas
    surf = pygame.Surface((100, 100))
    draw_arrow_left_icon(surf, (30, 30), 24, (255, 255, 255))
    draw_close_circle_icon(surf, (60, 60), 24, (255, 255, 255))

    # Failure path 1: Empty icon name raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: Icon name must not be empty"):
        get_icon_surface("", 32, (0, 0, 0))

    # Failure path 2: Non-positive size raises ValueError
    with pytest.raises(ValueError, match="CRITICAL: Icon size must be positive"):
        get_icon_surface("close", 0, (0, 0, 0))
    with pytest.raises(ValueError, match="CRITICAL: Icon size must be positive"):
        get_icon_surface("close", -5, (0, 0, 0))

    # Failure path 3: Missing icon file raises FileNotFoundError
    with patch("src.ui_icons.get_icon_svg_path", return_value=Path("non_existent_icon.svg")):
        with pytest.raises(FileNotFoundError, match="CRITICAL: Icon SVG not found"):
            get_icon_surface("unknown", 32, (0, 0, 0))

    # Failure path 4: Drawing functions validate radius/size > 0
    with pytest.raises(ValueError, match="CRITICAL: Radius must be positive"):
        draw_gear_icon(surf, (50, 50), 0, (0, 0, 0))
    with pytest.raises(ValueError, match="CRITICAL: Radius must be positive"):
        draw_close_circle_icon(surf, (50, 50), -1, (0, 0, 0))
    with pytest.raises(ValueError, match="CRITICAL: Size must be positive"):
        draw_arrow_left_icon(surf, (50, 50), 0, (0, 0, 0))


def test_init_hand_cursor() -> None:
    from unittest.mock import patch
    from src.ui_icons import get_hand_cursor_path, init_hand_cursor

    # Happy path: Cursor file exists and can be initialized in pygame
    path = get_hand_cursor_path()
    assert isinstance(path, Path)
    assert path.is_file()

    # Create dummy display for mouse cursor
    if not pygame.display.get_init():
        pygame.display.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((100, 100))

    cursor = init_hand_cursor()
    assert isinstance(cursor, pygame.cursors.Cursor)
    active = pygame.mouse.get_cursor()
    assert isinstance(active, pygame.cursors.Cursor)

    # Failure path: Missing hand cursor file raises FileNotFoundError
    with patch("src.ui_icons.get_hand_cursor_path", return_value=Path("non_existent_hand.svg")):
        with pytest.raises(FileNotFoundError, match="CRITICAL: Hand cursor SVG not found"):
            init_hand_cursor()


def test_draw_drop_shadow_happy_path() -> None:
    from src.ui_elements import draw_drop_shadow, UIButton

    surf = pygame.Surface((300, 200))
    rect = pygame.Rect(50, 50, 100, 50)
    draw_drop_shadow(surf, rect, border_radius=12)

    font = pygame.font.SysFont("arial", 20)
    btn = UIButton(rect=rect, text="Test")
    btn.render(surf, font, mouse_pos=(0, 0))


def test_draw_drop_shadow_invalid_dimensions_failure_path() -> None:
    from src.ui_elements import draw_drop_shadow

    surf = pygame.Surface((200, 200))
    with pytest.raises(ValueError, match="CRITICAL: Rect dimensions must be positive"):
        draw_drop_shadow(surf, pygame.Rect(10, 10, 0, 50), border_radius=10)
    with pytest.raises(ValueError, match="CRITICAL: Rect dimensions must be positive"):
        draw_drop_shadow(surf, pygame.Rect(10, 10, 50, -5), border_radius=10)


def test_draw_drop_shadow_negative_radius_failure_path() -> None:
    from src.ui_elements import draw_drop_shadow

    surf = pygame.Surface((200, 200))
    with pytest.raises(ValueError, match="CRITICAL: Border radius cannot be negative"):
        draw_drop_shadow(surf, pygame.Rect(10, 10, 50, 50), border_radius=-1)


def test_ui_checkbox_drop_shadow_happy_path() -> None:
    from src.ui_elements import UICheckbox

    surf = pygame.Surface((300, 300))
    surf.fill((255, 255, 255))
    font = pygame.font.SysFont("segoeui", 20)

    box = UICheckbox(rect=pygame.Rect(50, 50, 46, 46), label="A", checked=False)
    box.render(surf, font, mouse_pos=(0, 0))

    # A pixel just below the bottom edge (offset_y shadow) should be darkened by drop shadow
    shadow_pixel = surf.get_at((73, 50 + 46 + 1))
    assert (shadow_pixel.r, shadow_pixel.g, shadow_pixel.b) != (255, 255, 255)
    assert shadow_pixel.r < 255 and shadow_pixel.g < 255 and shadow_pixel.b < 255


def test_ui_checkbox_toggle_and_click_failure_paths() -> None:
    from src.ui_elements import UICheckbox

    box = UICheckbox(rect=pygame.Rect(50, 50, 46, 46), label="B", checked=False)
    assert box.checked is False
    box.toggle()
    assert box.checked is True

    # Failure path 1: Out of bounds click returns False
    assert box.is_clicked((0, 0)) is False
    assert box.is_clicked((200, 200)) is False

    # Failure path 2: Border edge outside bounds returns False
    assert box.is_clicked((49, 50)) is False
    assert box.is_clicked((50, 49)) is False


def test_svg_play_and_check_icons() -> None:
    from src.ui_icons import draw_check_icon, draw_play_icon, get_icon_surface
    from src.ui_elements import UICheckbox

    surf = pygame.Surface((200, 200))
    # Happy paths
    draw_play_icon(surf, (50, 50), 24, (255, 255, 255))
    draw_check_icon(surf, (100, 50), 20, (255, 255, 255))

    p_surf = get_icon_surface("play", 32, (255, 255, 255))
    assert p_surf.get_size() == (32, 32)
    c_surf = get_icon_surface("check", 32, (255, 255, 255))
    assert c_surf.get_size() == (32, 32)

    # Wide checkbox with checkmark
    font = pygame.font.SysFont("segoeui", 16)
    wide_box = UICheckbox(rect=pygame.Rect(10, 10, 150, 40), label="Mode Test", checked=True)
    wide_box.render(surf, font, mouse_pos=(0, 0))

    # Failure paths
    with pytest.raises(ValueError, match="CRITICAL: Play icon size must be positive"):
        draw_play_icon(surf, (50, 50), 0, (0, 0, 0))

    with pytest.raises(ValueError, match="CRITICAL: Check icon size must be positive"):
        draw_check_icon(surf, (50, 50), -10, (0, 0, 0))


def test_get_aa_rounded_rect_surface_happy_path() -> None:
    from src.ui_elements import get_aa_rounded_rect_surface

    surf = get_aa_rounded_rect_surface(100, 60, border_radius=15, bg_color=(20, 20, 25))
    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (100, 60)

    # Verify cache returns the exact same surface instance
    surf2 = get_aa_rounded_rect_surface(100, 60, border_radius=15, bg_color=(20, 20, 25))
    assert surf is surf2

    # Bordered version
    surf_bordered = get_aa_rounded_rect_surface(
        80, 80, border_radius=20, bg_color=(255, 255, 255), border_color=(20, 20, 25), border_width=3
    )
    assert surf_bordered.get_size() == (80, 80)


def test_get_aa_rounded_rect_surface_failure_paths() -> None:
    from src.ui_elements import get_aa_rounded_rect_surface

    # Failure path 1: Non-positive dimensions
    with pytest.raises(ValueError, match="CRITICAL: Dimensions must be positive"):
        get_aa_rounded_rect_surface(0, 50, border_radius=10, bg_color=(0, 0, 0))

    with pytest.raises(ValueError, match="CRITICAL: Dimensions must be positive"):
        get_aa_rounded_rect_surface(50, -5, border_radius=10, bg_color=(0, 0, 0))

    # Failure path 2: Negative border radius
    with pytest.raises(ValueError, match="CRITICAL: border_radius cannot be negative"):
        get_aa_rounded_rect_surface(50, 50, border_radius=-2, bg_color=(0, 0, 0))

    # Failure path 3: Negative border width
    with pytest.raises(ValueError, match="CRITICAL: border_width cannot be negative"):
        get_aa_rounded_rect_surface(50, 50, border_radius=10, bg_color=(0, 0, 0), border_width=-1)







