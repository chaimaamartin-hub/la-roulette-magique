import colorsys
import math
from typing import Literal
import pygame

from src.ui_elements import draw_drop_shadow, get_aa_rounded_rect_surface

AnimationState = Literal["FLYING_IN", "IDLE", "RAINBOW_FLASH", "RED_FLASH", "FLYING_OUT"]


RAINBOW_12_HUES: tuple[float, ...] = (
    0.00, 0.05, 0.09, 0.14, 0.22, 0.33, 0.45, 0.53, 0.60, 0.68, 0.78, 0.90,
)


def ease_out_cubic(t: float) -> float:
    clamped = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - clamped) ** 3


def compute_shake_offset(state_time: float, duration: float) -> int:
    if duration <= 0.0:
        raise ValueError("CRITICAL: duration must be positive.")
    if state_time < 0.0 or math.isnan(state_time):
        raise ValueError("CRITICAL: state_time must be non-negative.")
    if state_time >= duration:
        return 0
    decay = 1.0 - (state_time / duration)
    return int(round(10.0 * decay * math.sin(state_time * 45.0)))


def sample_rainbow_band_color(
    band_pos: float,
    saturation: float,
    value: float,
    feather: float,
) -> tuple[int, int, int]:
    if not isinstance(band_pos, (int, float)) or math.isnan(band_pos):
        raise ValueError("CRITICAL: band_pos must be a valid number.")
    if not (0.0 <= saturation <= 1.0) or not (0.0 <= value <= 1.0):
        raise ValueError("CRITICAL: saturation and value must be in [0.0, 1.0].")
    if not (0.0 <= feather < 1.0):
        raise ValueError("CRITICAL: feather must be in [0.0, 1.0).")

    n = len(RAINBOW_12_HUES)
    idx = int(math.floor(band_pos)) % n
    frac = band_pos - math.floor(band_pos)

    r1, g1, b1 = colorsys.hsv_to_rgb(RAINBOW_12_HUES[idx], saturation, value)
    if feather > 0.0 and frac > 1.0 - feather:
        t = (frac - (1.0 - feather)) / feather
        t = t * t * (3.0 - 2.0 * t)
        r2, g2, b2 = colorsys.hsv_to_rgb(RAINBOW_12_HUES[(idx + 1) % n], saturation, value)
        r = r1 + (r2 - r1) * t
        g = g1 + (g2 - g1) * t
        b = b1 + (b2 - b1) * t
    else:
        r, g, b = r1, g1, b1

    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


class Card:
    def __init__(
        self,
        symbol: str,
        index: int,
        target_rect: pygame.Rect,
        screen_width: int,
        entry_delay: float = 0.08,
    ) -> None:
        self.symbol: str = symbol
        self.index: int = index
        self.target_rect: pygame.Rect = target_rect
        self.screen_width: int = screen_width
        self.entry_delay: float = index * entry_delay

        self.current_x: float = float(-target_rect.width - 20)
        self.current_y: float = float(target_rect.y)
        self.width: int = target_rect.width
        self.height: int = target_rect.height

        self.state: AnimationState = "FLYING_IN"
        self.is_wrong: bool = False
        self.is_correct: bool = False
        self.state_time: float = 0.0
        self.correct_anim_time: float = 0.0
        self.hover_progress: float = 0.0
        self.fly_in_duration: float = 0.5
        self.fly_out_duration: float = 0.5
        self.rainbow_duration: float = 0.8
        self.red_flash_duration: float = 0.4

    def update(self, dt: float) -> None:
        self.state_time += dt
        if self.is_correct:
            self.correct_anim_time += dt
            self.hover_progress = 0.0
        elif self.is_wrong:
            self.hover_progress = 0.0

        if self.state == "FLYING_IN":
            if self.state_time >= self.entry_delay:
                progress = (self.state_time - self.entry_delay) / self.fly_in_duration
                if progress >= 1.0:
                    self.current_x = float(self.target_rect.x)
                    self.state = "IDLE"
                    self.state_time = 0.0
                else:
                    t = ease_out_cubic(progress)
                    start_x = -self.width - 20
                    self.current_x = start_x + (self.target_rect.x - start_x) * t

        elif self.state == "FLYING_OUT":
            delay = self.index * 0.08
            if self.state_time >= delay:
                progress = (self.state_time - delay) / self.fly_out_duration
                if progress >= 1.0:
                    self.current_x = float(self.screen_width + self.width + 20)
                else:
                    t = ease_out_cubic(progress)
                    end_x = self.screen_width + self.width + 20
                    self.current_x = self.target_rect.x + (end_x - self.target_rect.x) * t

        elif self.state == "RAINBOW_FLASH":
            if self.state_time >= self.rainbow_duration:
                self.state = "IDLE"
                self.state_time = 0.0

        elif self.state == "RED_FLASH":
            if self.state_time >= self.red_flash_duration:
                self.state = "IDLE"
                self.state_time = 0.0

    def trigger_rainbow(self) -> None:
        self.is_correct = True
        self.state = "RAINBOW_FLASH"
        self.state_time = 0.0
        self.correct_anim_time = 0.0
        self.hover_progress = 0.0

    def trigger_red_flash(self) -> None:
        self.is_wrong = True
        self.state = "RED_FLASH"
        self.state_time = 0.0
        self.hover_progress = 0.0

    def trigger_fly_out(self) -> None:
        self.state = "FLYING_OUT"
        self.state_time = 0.0

    def get_current_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.current_x), int(self.current_y), self.width, self.height)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        if self.is_wrong or self.state not in ("IDLE", "RED_FLASH"):
            return False
        rect = self.get_current_rect()
        raise_amount = max(5, min(10, self.height // 26))
        hit_rect = pygame.Rect(rect.x, rect.y - raise_amount, rect.width, rect.height + raise_amount)
        return hit_rect.collidepoint(pos)

    def _render_rainbow_card(
        self,
        surface: pygame.Surface,
        draw_rect: pygame.Rect,
        radius: int,
        text_surf: pygame.Surface,
        text_pos: tuple[int, int],
    ) -> None:
        if draw_rect.width <= 0 or draw_rect.height <= 0:
            raise ValueError("CRITICAL: draw_rect dimensions must be positive.")

        w, h = draw_rect.width, draw_rect.height
        flash_dur = self.rainbow_duration
        t_anim = self.correct_anim_time

        if t_anim <= flash_dur:
            tone = 0.0
            phase_offset = (t_anim / flash_dur) * 12.0
        else:
            extra_t = t_anim - flash_dur
            tone = min(1.0, extra_t / 0.25)
            phase_offset = 12.0 + extra_t * 4.0

        sat = 0.90 - (0.90 - 0.58) * tone
        val = 0.95 - (0.95 - 0.86) * tone
        bg_opacity = 0.10 - (0.10 - 0.06) * tone
        border_width = int(round(7.0 - (7.0 - 5.0) * tone))
        band_span_px = max(1.0, h * 0.30)

        fg_pattern = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_pattern = pygame.Surface((w, h), pygame.SRCALPHA)

        for u in range(w + h):
            band_pos = (u / band_span_px) - phase_offset
            r, g, b = sample_rainbow_band_color(band_pos, sat, val, 0.35)
            bg_col = (
                int(round(255 * (1.0 - bg_opacity) + r * bg_opacity)),
                int(round(255 * (1.0 - bg_opacity) + g * bg_opacity)),
                int(round(255 * (1.0 - bg_opacity) + b * bg_opacity)),
                255,
            )
            pygame.draw.line(fg_pattern, (r, g, b, 255), (u, 0), (0, u), 2)
            pygame.draw.line(bg_pattern, bg_col, (u, 0), (0, u), 2)

        card_mask = get_aa_rounded_rect_surface(w, h, radius, (255, 255, 255))
        bg_pattern.blit(card_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        fg_mask = get_aa_rounded_rect_surface(w, h, radius, None, (255, 255, 255), border_width).copy()
        fg_mask.blit(text_surf, (text_pos[0] - draw_rect.x, text_pos[1] - draw_rect.y))
        fg_pattern.blit(fg_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        bg_pattern.blit(fg_pattern, (0, 0))
        surface.blit(bg_pattern, draw_rect.topleft)

    def render(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        cap_offset: float | None = None,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        rect = self.get_current_rect()
        raise_amount = max(5, min(10, self.height // 26))
        hit_rect = pygame.Rect(rect.x, rect.y - raise_amount, rect.width, rect.height + raise_amount)
        is_hovered = mouse_pos is not None and hit_rect.collidepoint(mouse_pos)
        can_hover = self.state == "IDLE" and not self.is_wrong and not self.is_correct

        target_hover = 1.0 if (is_hovered and can_hover) else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * 0.35
        if abs(self.hover_progress - target_hover) < 0.01:
            self.hover_progress = target_hover

        scale = 1.0 + 0.02 * self.hover_progress
        if self.is_correct:
            if self.state == "RAINBOW_FLASH":
                t = min(1.0, self.state_time / 0.15)
                scale = 1.0 + 0.10 * (1.0 - (1.0 - t) ** 3)
            elif self.state == "IDLE":
                scale = 1.06 + 0.02 * math.sin(self.correct_anim_time * 4.0)
            elif self.state == "FLYING_OUT":
                scale = 1.10

        shake_x = compute_shake_offset(self.state_time, self.red_flash_duration) if self.state == "RED_FLASH" else 0
        elev_y = -int(round(raise_amount * self.hover_progress))
        base_rect = rect.move(shake_x, elev_y)

        if scale > 1.001:
            extra_w = int(round(rect.width * (scale - 1.0)))
            extra_h = int(round(rect.height * (scale - 1.0)))
            draw_rect = base_rect.inflate(extra_w, extra_h)
        else:
            draw_rect = base_rect

        radius = min(28, draw_rect.width // 6)
        shadow_offset_y = 6 if self.is_correct else int(round(4 + (raise_amount + 1) * self.hover_progress))
        draw_drop_shadow(surface, draw_rect, radius, offset_y=shadow_offset_y, blur_pad=10)

        render_text_col = (255, 255, 255) if (self.state == "RAINBOW_FLASH" or self.is_correct) else (34, 34, 34)
        if self.is_wrong and self.state != "RED_FLASH":
            render_text_col = (170, 170, 175)
        elif self.state == "RED_FLASH":
            factor = max(0.0, min(1.0, 1.0 - (self.state_time / self.red_flash_duration)))
            render_text_col = (
                int(170 - (170 - 34) * (1.0 - factor)),
                int(170 - (170 - 34) * (1.0 - factor)),
                int(175 - (175 - 34) * (1.0 - factor)),
            )

        text_surf = font.render(self.symbol, True, render_text_col)
        if scale > 1.001:
            scaled_tw = max(1, int(round(text_surf.get_width() * scale)))
            scaled_th = max(1, int(round(text_surf.get_height() * scale)))
            text_surf = pygame.transform.smoothscale(text_surf, (scaled_tw, scaled_th))

        text_x = draw_rect.centerx - text_surf.get_width() // 2
        if cap_offset is not None:
            text_y = int(draw_rect.centery - cap_offset * scale)
        else:
            text_y = draw_rect.centery - text_surf.get_height() // 2

        if self.state == "RAINBOW_FLASH" or self.is_correct:
            self._render_rainbow_card(surface, draw_rect, radius, text_surf, (text_x, text_y))
            return

        if self.is_wrong and self.state != "RED_FLASH":
            bg_color = (235, 235, 238)
            border_color = (205, 205, 212)
            border_width = 3
        elif is_hovered and can_hover:
            bg_color = (255, 252, 220)
            border_color = (220, 210, 160)
            border_width = 4
        elif self.state == "RED_FLASH":
            factor = max(0.0, min(1.0, 1.0 - (self.state_time / self.red_flash_duration)))
            bg_color = (
                int(235 + (255 - 235) * factor),
                int(235 - (235 - 77) * factor),
                int(238 - (238 - 77) * factor),
            )
            border_color = (
                int(205 + (255 - 205) * factor),
                int(205 - (205 - 77) * factor),
                int(212 - (212 - 77) * factor),
            )
            border_width = 4
        else:
            bg_color = (255, 255, 255)
            border_color = (200, 200, 210)
            border_width = 4

        card_body = get_aa_rounded_rect_surface(
            draw_rect.width, draw_rect.height, radius, bg_color, border_color, border_width
        )
        surface.blit(card_body, draw_rect.topleft)
        inner_rect = draw_rect.inflate(-border_width * 2, -border_width * 2)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(surface, bg_color, inner_rect, border_radius=max(0, radius - border_width))
        surface.blit(text_surf, (text_x, text_y))
