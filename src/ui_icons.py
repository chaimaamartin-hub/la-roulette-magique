from pathlib import Path
import sys
import pygame

_font_cache: dict[int, pygame.font.Font] = {}


def get_symbol_font(size: int) -> pygame.font.Font:
    if size <= 0:
        raise ValueError("CRITICAL: Font size must be greater than 0.")
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(["segoeuisymbol", "segoeui", "arial"], size)
    return _font_cache[size]


def render_unicode_symbol(
    surface: pygame.Surface,
    center: tuple[int, int],
    symbol: str,
    size: int,
    color: tuple[int, int, int],
) -> None:
    if not symbol:
        raise ValueError("CRITICAL: Symbol must not be empty.")
    font = get_symbol_font(size)
    text_surf = font.render(symbol, True, color)
    ink_rect = text_surf.get_bounding_rect()

    # Optical centering based on ink pixels
    if ink_rect.width > 0 and ink_rect.height > 0:
        blit_pos = (center[0] - ink_rect.centerx, center[1] - ink_rect.centery)
    else:
        text_rect = text_surf.get_rect(center=center)
        blit_pos = text_rect.topleft

    surface.blit(text_surf, blit_pos)


def draw_play_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    render_unicode_symbol(surface, center, "▶", size, color)


import io
_icon_cache: dict[tuple[str, int, tuple[int, int, int]], pygame.Surface] = {}

_BUILTIN_SVGS: dict[str, str] = {
    "arrow_left": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100" height="100">'
        '<path d="M19 12H5 M11 6L5 12L11 18" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
        '</svg>'
    ),
    "close": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100" height="100">'
        '<line x1="5" y1="5" x2="19" y2="19" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>'
        '<line x1="19" y1="5" x2="5" y2="19" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>'
        '</svg>'
    ),
}


def get_icon_svg_path(name: str) -> Path:
    if not name:
        raise ValueError("CRITICAL: Icon name must not be empty.")
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets" / "images" / "icons" / f"{name}.svg"


def get_gear_svg_path() -> Path:
    return get_icon_svg_path("gear")


def get_gear_surface(size: int, color: tuple[int, int, int]) -> pygame.Surface:
    if size <= 0:
        raise ValueError(f"CRITICAL: Gear size must be positive, got {size}")

    key = ("gear", size, color)
    if key in _icon_cache:
        return _icon_cache[key]

    svg_path = get_gear_svg_path()
    if not svg_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Gear SVG not found at {svg_path}")

    loaded = pygame.image.load(str(svg_path))
    scaled = pygame.transform.smoothscale(loaded, (size, size))
    if color != (255, 255, 255):
        scaled.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

    _icon_cache[key] = scaled
    return scaled


def get_icon_surface(name: str, size: int, color: tuple[int, int, int]) -> pygame.Surface:
    if not name:
        raise ValueError("CRITICAL: Icon name must not be empty.")
    if size <= 0:
        raise ValueError(f"CRITICAL: Icon size must be positive, got {size}")
    if name == "gear":
        return get_gear_surface(size, color)

    key = (name, size, color)
    if key in _icon_cache:
        return _icon_cache[key]

    if name in _BUILTIN_SVGS:
        loaded = pygame.image.load(io.BytesIO(_BUILTIN_SVGS[name].encode("utf-8")))
    else:
        svg_path = get_icon_svg_path(name)
        if not svg_path.is_file():
            raise FileNotFoundError(f"CRITICAL: Icon SVG not found at {svg_path}")
        loaded = pygame.image.load(str(svg_path))

    scaled = pygame.transform.smoothscale(loaded, (size, size))
    if color != (255, 255, 255):
        scaled.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

    _icon_cache[key] = scaled
    return scaled


def draw_gear_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    if radius <= 0:
        raise ValueError(f"CRITICAL: Radius must be positive, got {radius}")
    size = max(16, int(radius * 1.3))
    gear_surf = get_gear_surface(size, color)
    rect = gear_surf.get_rect(center=center)
    surface.blit(gear_surf, rect)


def draw_close_circle_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    if radius <= 0:
        raise ValueError(f"CRITICAL: Radius must be positive, got {radius}")
    size = max(16, int(radius * 1.3))
    icon_surf = get_icon_surface("close", size, color)
    rect = icon_surf.get_rect(center=center)
    surface.blit(icon_surf, rect)


def draw_arrow_left_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    if size <= 0:
        raise ValueError(f"CRITICAL: Size must be positive, got {size}")
    icon_sz = max(16, int(size * 1.3))
    icon_surf = get_icon_surface("arrow_left", icon_sz, color)
    rect = icon_surf.get_rect(center=center)
    surface.blit(icon_surf, rect)


def draw_progress_stars(
    surface: pygame.Surface,
    center_pos: tuple[int, int],
    round_results: list[bool],
    total_rounds: int = 10,
    radius: int = 16,
    spacing: int = 44,
    filled_color: tuple[int, int, int] = (235, 165, 0),
    empty_color: tuple[int, int, int] = (20, 20, 25),
    unplayed_color: tuple[int, int, int] = (190, 190, 200),
    star_y_offsets: list[int] | None = None,
) -> None:
    cx, cy = center_pos
    total_w = (total_rounds - 1) * spacing
    start_x = cx - total_w // 2
    font_sz = max(18, int(radius * 2.2))

    for i in range(total_rounds):
        x = start_x + i * spacing
        y = cy + (star_y_offsets[i] if star_y_offsets and i < len(star_y_offsets) else 0)
        if i < len(round_results):
            if round_results[i]:
                # Correct round: Golden yellow filled star ★
                render_unicode_symbol(surface, (x, y), "★", font_sz, filled_color)
            else:
                # Wrong initial attempt: Empty star ☆
                render_unicode_symbol(surface, (x, y), "☆", font_sz, empty_color)
        else:
            # Unplayed round: Grey empty star ☆
            render_unicode_symbol(surface, (x, y), "☆", font_sz, unplayed_color)


def draw_progress_circles(
    surface: pygame.Surface,
    center_pos: tuple[int, int],
    round_results: list[bool],
    total_rounds: int = 10,
    radius: int = 16,
    spacing: int = 44,
) -> None:
    draw_progress_stars(
        surface=surface,
        center_pos=center_pos,
        round_results=round_results,
        total_rounds=total_rounds,
        radius=radius,
        spacing=spacing,
    )


def get_hand_cursor_path() -> Path:
    return get_icon_svg_path("hand_cursor")


def init_hand_cursor() -> pygame.cursors.Cursor:
    cursor_path = get_hand_cursor_path()
    if not cursor_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Hand cursor SVG not found at {cursor_path}")
    surf = pygame.image.load(str(cursor_path))
    cursor = pygame.cursors.Cursor((4, 4), surf)
    pygame.mouse.set_cursor(cursor)
    return cursor

