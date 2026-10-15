from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.star_renderer import (
    compute_star_points,
    draw_progress_stars,
    draw_subtle_sparkle,
    get_cached_star_surface,
)


@pytest.fixture(scope="module", autouse=True)
def init_pygame() -> None:
    pygame.init()


def test_compute_star_points_happy_path() -> None:
    pts = compute_star_points((100.0, 100.0), outer_radius=20.0, inner_radius=8.8)
    assert len(pts) == 10
    # Top point should be directly above center: x == 100, y == 80
    assert pytest.approx(pts[0][0], abs=1e-3) == 100.0
    assert pytest.approx(pts[0][1], abs=1e-3) == 80.0


def test_compute_star_points_failure_paths() -> None:
    # Failure path 1: outer_radius <= 0
    with pytest.raises(ValueError, match="CRITICAL: outer_radius must be positive"):
        compute_star_points((0.0, 0.0), outer_radius=-5.0, inner_radius=2.0)

    # Failure path 2: inner_radius <= 0
    with pytest.raises(ValueError, match="CRITICAL: inner_radius must be positive"):
        compute_star_points((0.0, 0.0), outer_radius=10.0, inner_radius=0.0)

    # Failure path 3: inner_radius >= outer_radius
    with pytest.raises(ValueError, match="CRITICAL: inner_radius must be smaller than outer_radius"):
        compute_star_points((0.0, 0.0), outer_radius=10.0, inner_radius=15.0)


def test_cached_star_surfaces_and_states() -> None:
    for state in ("FILLED", "WRONG", "UNPLAYED"):
        surf, cx, cy = get_cached_star_surface(18, state)
        assert isinstance(surf, pygame.Surface)
        assert cx > 0 and cy > 0
        # Caching returns identical object
        surf2, _, _ = get_cached_star_surface(18, state)
        assert surf is surf2


def test_get_star_svg_content_happy_and_failure_paths() -> None:
    from src.star_renderer import get_star_svg_content

    # Happy paths
    for st in ("FILLED", "WRONG", "UNPLAYED"):
        content = get_star_svg_content(st)
        assert "<svg" in content
        assert "<polygon" in content

    # Failure path: unknown state
    with pytest.raises(ValueError, match="CRITICAL: Unknown star state 'INVALID'"):
        get_star_svg_content("INVALID")


def test_cached_star_surface_failure_paths() -> None:
    # Failure path 1: Non-positive radius
    with pytest.raises(ValueError, match="CRITICAL: radius must be positive"):
        get_cached_star_surface(0, "FILLED")

    # Failure path 2: Unknown state
    with pytest.raises(ValueError, match="CRITICAL: Unknown star state"):
        get_cached_star_surface(16, "UNKNOWN_STATE")


def test_draw_progress_stars_happy_path() -> None:
    surf = pygame.Surface((600, 150))
    surf.fill((255, 255, 255))
    results = [True, False, True]

    # Render at various animation times
    for t in (0.0, 0.5, 1.2, 3.8):
        draw_progress_stars(
            surface=surf,
            center_pos=(300, 75),
            round_results=results,
            total_rounds=10,
            radius=18,
            spacing=48,
            anim_time=t,
        )

    # Test with star_y_offsets
    offsets = [0, -5, 10, 0, 0, 0, 0, 0, 0, 0]
    draw_progress_stars(
        surface=surf,
        center_pos=(300, 75),
        round_results=results,
        total_rounds=10,
        radius=18,
        spacing=48,
        star_y_offsets=offsets,
    )


def test_draw_progress_stars_failure_paths() -> None:
    surf = pygame.Surface((200, 100))

    # Failure path 1: total_rounds <= 0
    with pytest.raises(ValueError, match="CRITICAL: total_rounds must be positive"):
        draw_progress_stars(surf, (100, 50), [], total_rounds=0)

    # Failure path 2: radius <= 0
    with pytest.raises(ValueError, match="CRITICAL: radius must be positive"):
        draw_progress_stars(surf, (100, 50), [], radius=-10)

    # Failure path 3: spacing <= 0
    with pytest.raises(ValueError, match="CRITICAL: spacing must be positive"):
        draw_progress_stars(surf, (100, 50), [], spacing=0)


def test_draw_subtle_sparkle_boundaries() -> None:
    surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    # Outside range [0.0, 1.0] should be a clean no-op
    draw_subtle_sparkle(surf, (50, 50), 20.0, progress=-0.5)
    draw_subtle_sparkle(surf, (50, 50), 20.0, progress=1.5)
    # Midpoint peak sparkle
    draw_subtle_sparkle(surf, (50, 50), 20.0, progress=0.5)
