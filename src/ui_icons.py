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


def draw_gear_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    render_unicode_symbol(surface, center, "⛭", int(radius * 1.8), color)


def draw_close_circle_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    render_unicode_symbol(surface, center, "✕", int(radius * 1.8), color)


def draw_arrow_left_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    render_unicode_symbol(surface, center, "←", size, color)


def draw_progress_circles(
    surface: pygame.Surface,
    center_pos: tuple[int, int],
    round_results: list[bool],
    total_rounds: int = 10,
    radius: int = 16,
    spacing: int = 44,
) -> None:
    cx, cy = center_pos
    total_w = (total_rounds - 1) * spacing
    start_x = cx - total_w // 2
    font_sz = max(18, int(radius * 2.2))

    for i in range(total_rounds):
        x = start_x + i * spacing
        if i < len(round_results):
            if round_results[i]:
                # Correct: Solid black circle ●
                render_unicode_symbol(surface, (x, cy), "●", font_sz, (20, 20, 25))
            else:
                # Wrong initial attempt: Hollow circle ○
                render_unicode_symbol(surface, (x, cy), "○", font_sz, (20, 20, 25))
        else:
            # Unplayed round: Grey hollow circle ○
            render_unicode_symbol(surface, (x, cy), "○", font_sz, (190, 190, 200))
