from typing import Literal
import pygame

from src.ui_icons import (
    draw_arrow_left_icon,
    draw_check_icon,
    draw_close_circle_icon,
    draw_gear_icon,
    draw_play_icon,
    draw_progress_circles,
    draw_progress_stars,
)

IconType = Literal["PLAY", "GEAR", "EXIT", "ARROW_LEFT"]


_aa_rect_cache: dict[tuple[int, int, int, tuple[int, int, int] | None, tuple[int, int, int] | None, int], pygame.Surface] = {}
_shadow_cache: dict[tuple[int, int, int, int, int], tuple[pygame.Surface, int]] = {}


def get_aa_rounded_rect_surface(
    width: int,
    height: int,
    border_radius: int,
    bg_color: tuple[int, int, int] | None,
    border_color: tuple[int, int, int] | None = None,
    border_width: int = 0,
    aa_scale: int = 3,
) -> pygame.Surface:
    if width <= 0 or height <= 0:
        raise ValueError(f"CRITICAL: Dimensions must be positive, got ({width}, {height})")
    if border_radius < 0:
        raise ValueError(f"CRITICAL: border_radius cannot be negative, got {border_radius}")
    if border_width < 0:
        raise ValueError(f"CRITICAL: border_width cannot be negative, got {border_width}")

    key = (width, height, border_radius, bg_color, border_color, border_width)
    if key in _aa_rect_cache:
        return _aa_rect_cache[key]

    sw, sh = width * aa_scale, height * aa_scale
    srad = border_radius * aa_scale
    sbw = border_width * aa_scale

    surf_hi = pygame.Surface((sw, sh), pygame.SRCALPHA)
    if bg_color is not None:
        pygame.draw.rect(surf_hi, bg_color, (0, 0, sw, sh), border_radius=srad)
    if border_color is not None and border_width > 0:
        pygame.draw.rect(surf_hi, border_color, (0, 0, sw, sh), width=sbw, border_radius=srad)

    surf = pygame.transform.smoothscale(surf_hi, (width, height))
    _aa_rect_cache[key] = surf
    return surf


def draw_drop_shadow(
    surface: pygame.Surface,
    rect: pygame.Rect,
    border_radius: int,
    offset_y: int = 3,
    blur_pad: int = 6,
) -> None:
    if rect.width <= 0 or rect.height <= 0:
        raise ValueError("CRITICAL: Rect dimensions must be positive")
    if border_radius < 0:
        raise ValueError("CRITICAL: Border radius cannot be negative")

    key = (rect.width, rect.height, border_radius, offset_y, blur_pad)
    if key not in _shadow_cache:
        w = rect.width + blur_pad * 2
        h = rect.height + blur_pad * 2 + offset_y
        scale = 0.5
        sw, sh = max(4, int(w * scale)), max(4, int(h * scale))
        s_pad = blur_pad * scale
        s_rad = border_radius * scale
        s_off = offset_y * scale
        s_w, s_h = rect.width * scale, rect.height * scale

        low_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(low_surf, (0, 0, 0, 16), pygame.Rect(s_pad, s_pad + s_off + 1, s_w, s_h), border_radius=int(s_rad))
        pygame.draw.rect(low_surf, (0, 0, 0, 30), pygame.Rect(s_pad, s_pad + s_off, s_w, s_h), border_radius=int(s_rad))
        shadow_surf = pygame.transform.smoothscale(low_surf, (w, h))
        _shadow_cache[key] = (shadow_surf, blur_pad)

    sh_surf, pad = _shadow_cache[key]
    surface.blit(sh_surf, (rect.x - pad, rect.y - pad))


def compute_button_rect(
    rect: pygame.Rect,
    hover_scale: float,
    is_pressed: bool,
) -> pygame.Rect:
    if rect.width <= 0 or rect.height <= 0:
        raise ValueError("CRITICAL: Button rect dimensions must be positive.")
    if hover_scale <= 0.0:
        raise ValueError("CRITICAL: hover_scale must be positive.")

    extra_w = int(round(rect.width * (hover_scale - 1.0)))
    extra_h = int(round(rect.height * (hover_scale - 1.0)))
    scaled_rect = rect.inflate(extra_w, extra_h)
    if is_pressed:
        scaled_rect = scaled_rect.move(0, 2)
    return scaled_rect


def _is_left_mouse_pressed() -> bool:
    if not pygame.get_init() or not pygame.display.get_init():
        return False
    try:
        return bool(pygame.mouse.get_pressed()[0])
    except Exception:
        return False


class UIButton:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        bg_color: tuple[int, int, int] = (20, 20, 25),
        hover_color: tuple[int, int, int] = (50, 50, 60),
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_radius: int = 20,
        border_color: tuple[int, int, int] | None = None,
        border_width: int = 0,
    ) -> None:
        self.rect: pygame.Rect = rect
        self.text: str = text
        self.bg_color: tuple[int, int, int] = bg_color
        self.hover_color: tuple[int, int, int] = hover_color
        self.text_color: tuple[int, int, int] = text_color
        self.border_radius: int = border_radius
        self.border_color: tuple[int, int, int] | None = border_color
        self.border_width: int = border_width
        self.hover_scale: float = 1.0

    def is_hovered(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def render(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        mouse_pos: tuple[int, int],
    ) -> None:
        hover = self.is_hovered(mouse_pos)
        target_scale = 1.05 if hover else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.35
        if abs(self.hover_scale - target_scale) < 0.002:
            self.hover_scale = target_scale

        is_pressed = hover and _is_left_mouse_pressed()
        draw_rect = compute_button_rect(self.rect, self.hover_scale, is_pressed)
        draw_drop_shadow(surface, draw_rect, self.border_radius, offset_y=2 if is_pressed else 3)
        color = self.hover_color if hover else self.bg_color

        btn_surf = get_aa_rounded_rect_surface(
            draw_rect.width, draw_rect.height, self.border_radius, color, self.border_color, self.border_width
        )
        surface.blit(btn_surf, draw_rect.topleft)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)


class UIIconButton:
    def __init__(
        self,
        rect: pygame.Rect,
        icon_type: IconType,
        bg_color: tuple[int, int, int] = (20, 20, 25),
        hover_color: tuple[int, int, int] = (50, 50, 60),
        icon_color: tuple[int, int, int] = (255, 255, 255),
        border_radius: int = 24,
        border_color: tuple[int, int, int] | None = None,
        border_width: int = 0,
    ) -> None:
        self.rect: pygame.Rect = rect
        self.icon_type: IconType = icon_type
        self.bg_color: tuple[int, int, int] = bg_color
        self.hover_color: tuple[int, int, int] = hover_color
        self.icon_color: tuple[int, int, int] = icon_color
        self.border_radius: int = border_radius
        self.border_color: tuple[int, int, int] | None = border_color
        self.border_width: int = border_width
        self.hover_scale: float = 1.0

    def is_hovered(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def render(self, surface: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        hover = self.is_hovered(mouse_pos)
        target_scale = 1.05 if hover else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.35
        if abs(self.hover_scale - target_scale) < 0.002:
            self.hover_scale = target_scale

        is_pressed = hover and _is_left_mouse_pressed()
        draw_rect = compute_button_rect(self.rect, self.hover_scale, is_pressed)
        draw_drop_shadow(surface, draw_rect, self.border_radius, offset_y=2 if is_pressed else 3)
        color = self.hover_color if hover else self.bg_color

        btn_surf = get_aa_rounded_rect_surface(
            draw_rect.width, draw_rect.height, self.border_radius, color, self.border_color, self.border_width
        )
        surface.blit(btn_surf, draw_rect.topleft)

        cx, cy = draw_rect.center
        icon_sz = min(draw_rect.width, draw_rect.height) // 2

        if self.icon_type == "PLAY":
            draw_play_icon(surface, (cx, cy), icon_sz, self.icon_color)
        elif self.icon_type == "GEAR":
            draw_gear_icon(surface, (cx, cy), icon_sz, self.icon_color)
        elif self.icon_type == "EXIT":
            draw_close_circle_icon(surface, (cx, cy), icon_sz, self.icon_color)
        elif self.icon_type == "ARROW_LEFT":
            draw_arrow_left_icon(surface, (cx, cy), icon_sz, self.icon_color)


class UICheckbox:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        checked: bool = False,
    ) -> None:
        self.rect: pygame.Rect = rect
        self.label: str = label
        self.checked: bool = checked

    def toggle(self) -> bool:
        self.checked = not self.checked
        return self.checked

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def render(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        mouse_pos: tuple[int, int],
    ) -> None:
        radius = max(6, self.rect.width // 4)
        offset_y = 2 if self.rect.width < 60 else 3
        draw_drop_shadow(surface, self.rect, radius, offset_y=offset_y)

        hover = self.rect.collidepoint(mouse_pos)
        if self.checked:
            bg = (20, 20, 25)
            border = (20, 20, 25)
            text_color = (255, 255, 255)
        else:
            bg = (240, 240, 245) if hover else (255, 255, 255)
            border = (140, 140, 150)
            text_color = (20, 20, 25)

        box_surf = get_aa_rounded_rect_surface(self.rect.width, self.rect.height, radius, bg, border, 2)
        surface.blit(box_surf, self.rect.topleft)

        text_surf = font.render(self.label, True, text_color)
        if self.checked and self.rect.width >= 100:
            icon_sz = max(14, int(self.rect.height * 0.40))
            spacing = 8
            total_content_w = icon_sz + spacing + text_surf.get_width()
            start_x = self.rect.centerx - total_content_w // 2
            draw_check_icon(surface, (start_x + icon_sz // 2, self.rect.centery), icon_sz, text_color)
            surface.blit(
                text_surf,
                (start_x + icon_sz + spacing, self.rect.centery - text_surf.get_height() // 2),
            )
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

