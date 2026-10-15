import io
import math
from pathlib import Path
import sys
import time
from typing import Sequence
import pygame

_star_cache: dict[tuple[int, str], tuple[pygame.Surface, int, int]] = {}

_BUILTIN_STAR_SVGS: dict[str, str] = {
    "FILLED": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200" height="200">'
        '<defs>'
        '<linearGradient id="goldGrad" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#FFF275" />'
        '<stop offset="35%" stop-color="#FFCE00" />'
        '<stop offset="100%" stop-color="#FF8A00" />'
        '</linearGradient>'
        '<linearGradient id="highlightGrad" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.75" />'
        '<stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0" />'
        '</linearGradient>'
        '</defs>'
        '<polygon points="50,6 63,34 94,39 71,62 77,93 50,78 23,93 29,62 6,39 37,34" '
        'fill="url(#goldGrad)" stroke="#D87800" stroke-width="5" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        '<polygon points="50,11 61,35 88,39 68,59 50,48 32,59 12,39 39,35" '
        'fill="url(#highlightGrad)"/>'
        '</svg>'
    ),
    "WRONG": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200" height="200">'
        '<polygon points="50,6 63,34 94,39 71,62 77,93 50,78 23,93 29,62 6,39 37,34" '
        'fill="#EAEAEA" stroke="#2D3142" stroke-width="5.5" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        '</svg>'
    ),
    "UNPLAYED": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200" height="200">'
        '<polygon points="50,6 63,34 94,39 71,62 77,93 50,78 23,93 29,62 6,39 37,34" '
        'fill="#FFFFFF" stroke="#C5C8D4" stroke-width="5" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        '</svg>'
    ),
}


def get_star_svg_content(state: str) -> str:
    if state not in _BUILTIN_STAR_SVGS:
        raise ValueError(f"CRITICAL: Unknown star state '{state}'.")
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    svg_path = base / "assets" / "images" / "icons" / f"star_{state.lower()}.svg"
    if svg_path.is_file():
        return svg_path.read_text(encoding="utf-8")
    return _BUILTIN_STAR_SVGS[state]


def compute_star_points(
    center: tuple[float, float],
    outer_radius: float,
    inner_radius: float,
) -> list[tuple[float, float]]:
    if outer_radius <= 0:
        raise ValueError("CRITICAL: outer_radius must be positive.")
    if inner_radius <= 0:
        raise ValueError("CRITICAL: inner_radius must be positive.")
    if inner_radius >= outer_radius:
        raise ValueError("CRITICAL: inner_radius must be smaller than outer_radius.")

    cx, cy = center
    points: list[tuple[float, float]] = []
    start_angle = -math.pi / 2.0
    step = math.pi / 5.0

    for i in range(10):
        angle = start_angle + i * step
        r = outer_radius if (i % 2 == 0) else inner_radius
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    return points


def get_cached_star_surface(radius: int, state: str) -> tuple[pygame.Surface, int, int]:
    if radius <= 0:
        raise ValueError(f"CRITICAL: radius must be positive, got {radius}.")
    if state not in ("FILLED", "WRONG", "UNPLAYED"):
        raise ValueError(f"CRITICAL: Unknown star state '{state}'.")

    key = (radius, state)
    if key in _star_cache:
        return _star_cache[key]

    target_sz = int(radius * 2.3)
    pad = int(radius * 0.7) + 6
    box_sz = target_sz + pad * 2

    svg_content = get_star_svg_content(state)
    raw_surf = pygame.image.load(io.BytesIO(svg_content.encode("utf-8")))
    scaled_star = pygame.transform.smoothscale(raw_surf, (target_sz, target_sz))

    # Silky-smooth ambient drop shadow using native SIMD gaussian blur
    shadow_surf = pygame.Surface((box_sz, box_sz), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(scaled_star)

    if state == "FILLED":
        shadow_col = (60, 35, 0, 85)
        dy = max(2, int(radius * 0.16))
    elif state == "WRONG":
        shadow_col = (0, 0, 0, 50)
        dy = max(1, int(radius * 0.12))
    else:
        shadow_col = (0, 0, 0, 32)
        dy = max(1, int(radius * 0.10))

    mask_surf = mask.to_surface(setcolor=shadow_col, unsetcolor=(0, 0, 0, 0))
    shadow_surf.blit(mask_surf, (pad, pad + dy))

    blur_r = max(2, int(radius * 0.22))
    blurred_shadow = pygame.transform.gaussian_blur(shadow_surf, blur_r)

    composite_surf = pygame.Surface((box_sz, box_sz), pygame.SRCALPHA)
    composite_surf.blit(blurred_shadow, (0, 0))
    composite_surf.blit(scaled_star, (pad, pad))

    scx = pad + target_sz // 2
    scy = pad + target_sz // 2

    result = (composite_surf, scx, scy)
    _star_cache[key] = result
    return result


def draw_subtle_sparkle(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: float,
    progress: float,
) -> None:
    if not (0.0 <= progress <= 1.0):
        return

    # Gentle bell curve: smooth fade-in and fade-out
    intensity = math.sin(progress * math.pi)
    alpha = int(170 * intensity)
    if alpha <= 0:
        return

    cx, cy = center
    ray_len = max(2.5, radius * (0.24 + 0.12 * intensity))
    ray_thickness = max(1.0, ray_len * 0.16)

    box_size = int(ray_len * 2.5) + 4
    sparkle_surf = pygame.Surface((box_size, box_size), pygame.SRCALPHA)
    scx, scy = box_size // 2, box_size // 2

    # Vertical diamond needle
    v_pts = [
        (scx, scy - ray_len),
        (scx + ray_thickness, scy),
        (scx, scy + ray_len),
        (scx - ray_thickness, scy),
    ]
    pygame.draw.polygon(sparkle_surf, (255, 255, 255, alpha), v_pts)

    # Horizontal diamond needle
    h_pts = [
        (scx - ray_len, scy),
        (scx, scy - ray_thickness),
        (scx + ray_len, scy),
        (scx, scy + ray_thickness),
    ]
    pygame.draw.polygon(sparkle_surf, (255, 255, 255, alpha), h_pts)

    # Soft glowing core
    center_glow_r = max(1, int(ray_len * 0.20))
    glow_alpha = min(255, int(alpha * 1.25))
    pygame.draw.circle(sparkle_surf, (255, 255, 255, glow_alpha), (scx, scy), center_glow_r)

    surface.blit(sparkle_surf, (cx - scx, cy - scy))


def draw_progress_stars(
    surface: pygame.Surface,
    center_pos: tuple[int, int],
    round_results: Sequence[bool],
    total_rounds: int = 10,
    radius: int = 16,
    spacing: int = 44,
    filled_color: tuple[int, int, int] = (255, 192, 10),
    empty_color: tuple[int, int, int] = (20, 20, 25),
    unplayed_color: tuple[int, int, int] = (195, 195, 205),
    star_y_offsets: list[int] | None = None,
    anim_time: float | None = None,
) -> None:
    if total_rounds <= 0:
        raise ValueError(f"CRITICAL: total_rounds must be positive, got {total_rounds}.")
    if radius <= 0:
        raise ValueError(f"CRITICAL: radius must be positive, got {radius}.")
    if spacing <= 0:
        raise ValueError(f"CRITICAL: spacing must be positive, got {spacing}.")

    t = time.time() if anim_time is None else anim_time
    cx, cy = center_pos
    total_w = (total_rounds - 1) * spacing
    start_x = cx - total_w // 2

    cycle_period = 4.0
    sparkle_dur = 0.80

    for i in range(total_rounds):
        x = start_x + i * spacing
        y_off = star_y_offsets[i] if (star_y_offsets is not None and i < len(star_y_offsets)) else 0
        y = cy + y_off

        if i < len(round_results):
            state = "FILLED" if round_results[i] else "WRONG"
        else:
            state = "UNPLAYED"

        surf, scx, scy = get_cached_star_surface(radius, state)
        surface.blit(surf, (x - scx, y - scy))

        # Sparkling occurs ONLY when the star is golden (filled out)
        if state == "FILLED":
            stagger = (i * 0.85) % cycle_period
            local_t = (t + stagger) % cycle_period
            if local_t < sparkle_dur:
                progress = local_t / sparkle_dur
                sparkle_cx = int(x + radius * 0.35)
                sparkle_cy = int(y - radius * 0.35)
                draw_subtle_sparkle(surface, (sparkle_cx, sparkle_cy), float(radius), progress)
