import io
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
    if size <= 0:
        raise ValueError(f"CRITICAL: Play icon size must be positive, got {size}")
    icon_sz = max(16, int(size * 1.3))
    icon_surf = get_icon_surface("play", icon_sz, color)
    ink = icon_surf.get_bounding_rect()
    blit_pos = (center[0] - ink.centerx, center[1] - ink.centery)
    surface.blit(icon_surf, blit_pos)


def draw_check_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    if size <= 0:
        raise ValueError(f"CRITICAL: Check icon size must be positive, got {size}")
    icon_sz = max(12, int(size * 1.2))
    icon_surf = get_icon_surface("check", icon_sz, color)
    rect = icon_surf.get_rect(center=center)
    surface.blit(icon_surf, rect)


_icon_cache: dict[tuple[str, int, tuple[int, int, int]], pygame.Surface] = {}

_BUILTIN_SVGS: dict[str, str] = {
    "play": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
        '<path d="M7.5 4.8C7.5 3.8 8.6 3.2 9.5 3.8L20.2 11.0C21.0 11.5 21.0 12.5 20.2 13.0L9.5 20.2C8.6 20.8 7.5 20.2 7.5 19.2Z" '
        'fill="#ffffff" stroke="#ffffff" stroke-width="1.5" stroke-linejoin="round"/>'
        '</svg>'
    ),
    "arrow_left": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
        '<path d="M19 12H5M12 19L5 12L12 5" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    ),
    "close": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
        '<path d="M18 6L6 18M6 6L18 18" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    ),
    "check": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
        '<path d="M20 6L9 17L4 12" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
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


from src.star_renderer import draw_progress_stars

draw_progress_circles = draw_progress_stars


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

