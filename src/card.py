import colorsys
import math
from typing import Literal
import pygame

AnimationState = Literal["FLYING_IN", "IDLE", "RAINBOW_FLASH", "RED_FLASH", "FLYING_OUT"]


def ease_out_cubic(t: float) -> float:
    clamped = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - clamped) ** 3


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
        self.fly_in_duration: float = 0.5
        self.fly_out_duration: float = 0.5
        self.rainbow_duration: float = 0.8
        self.red_flash_duration: float = 0.4

    def update(self, dt: float) -> None:
        self.state_time += dt
        if self.is_correct:
            self.correct_anim_time += dt

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

    def trigger_red_flash(self) -> None:
        self.is_wrong = True
        self.state = "RED_FLASH"
        self.state_time = 0.0

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

    def render(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        cap_offset: float | None = None,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        rect = self.get_current_rect()
        scale = 1.0
        if self.is_correct:
            if self.state == "RAINBOW_FLASH":
                t = min(1.0, self.state_time / 0.15)
                scale = 1.0 + 0.10 * (1.0 - (1.0 - t) ** 3)
            elif self.state == "IDLE":
                scale = 1.06 + 0.02 * math.sin(self.correct_anim_time * 4.0)
            elif self.state == "FLYING_OUT":
                scale = 1.10

        raise_amount = max(5, min(10, self.height // 26))
        hit_rect = pygame.Rect(rect.x, rect.y - raise_amount, rect.width, rect.height + raise_amount)
        is_hovered = mouse_pos is not None and hit_rect.collidepoint(mouse_pos)
        is_raised = is_hovered and self.state in ("IDLE", "FLYING_IN") and not self.is_wrong and not self.is_correct
        base_rect = rect.move(0, -raise_amount) if is_raised else rect

        if scale > 1.001:
            extra_w = int(round(rect.width * (scale - 1.0)))
            extra_h = int(round(rect.height * (scale - 1.0)))
            draw_rect = base_rect.inflate(extra_w, extra_h)
        else:
            draw_rect = base_rect

        if self.is_wrong and self.state != "RED_FLASH":
            bg_color = (235, 235, 238)
            border_color = (205, 205, 212)
            border_width = 3
            text_color = (170, 170, 175)
        elif is_hovered and self.state in ("IDLE", "FLYING_IN") and not self.is_correct:
            bg_color = (255, 252, 220)  # Very light yellow hover
            border_color = (220, 210, 160)
            border_width = 4
            text_color = (34, 34, 34)
        else:
            bg_color = (255, 255, 255)
            border_color = (200, 200, 210)
            border_width = 4
            text_color = (34, 34, 34)

        if self.state == "RED_FLASH":
            factor = 1.0 - (self.state_time / self.red_flash_duration)
            factor = max(0.0, min(1.0, factor))
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
            text_color = (
                int(170 - (170 - 34) * (1.0 - factor)),
                int(170 - (170 - 34) * (1.0 - factor)),
                int(175 - (175 - 34) * (1.0 - factor)),
            )

        elif self.state == "RAINBOW_FLASH":
            hue = (self.state_time / self.rainbow_duration) % 1.0
            rgb_f = colorsys.hsv_to_rgb(hue, 0.88, 0.95)
            rainbow_col = (int(rgb_f[0] * 255), int(rgb_f[1] * 255), int(rgb_f[2] * 255))
            # Very light pastel background tint
            bg_f = colorsys.hsv_to_rgb(hue, 0.18, 1.0)
            bg_color = (int(bg_f[0] * 255), int(bg_f[1] * 255), int(bg_f[2] * 255))
            border_color = rainbow_col
            border_width = 7
            text_color = rainbow_col

        elif self.is_correct:
            # Ongoing gentle pastel animation after initial rainbow flash
            hue = (self.correct_anim_time * 0.20) % 1.0
            pulse = 0.5 + 0.5 * math.sin(self.correct_anim_time * 3.0)
            sat = 0.12 + 0.06 * pulse
            bg_f = colorsys.hsv_to_rgb(hue, sat, 1.0)
            bg_color = (int(bg_f[0] * 255), int(bg_f[1] * 255), int(bg_f[2] * 255))

            border_f = colorsys.hsv_to_rgb(hue, 0.50, 0.88)
            border_color = (int(border_f[0] * 255), int(border_f[1] * 255), int(border_f[2] * 255))
            border_width = 5
            text_color = (30, 30, 35)

        radius = min(28, draw_rect.width // 6)

        # Drop shadow beneath the card
        shadow_pad = 16
        shadow_surf = pygame.Surface(
            (draw_rect.width + shadow_pad * 2, draw_rect.height + shadow_pad * 2 + 16),
            pygame.SRCALPHA,
        )
        if self.is_correct:
            sy, a1, a2 = shadow_pad + 6, 18, 32
        elif is_raised:
            sy, a1, a2 = shadow_pad + raise_amount + 5, 15, 28
        else:
            sy, a1, a2 = shadow_pad + 4, 15, 25

        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, a1),
            pygame.Rect(shadow_pad, sy + 3, draw_rect.width, draw_rect.height),
            border_radius=radius,
        )
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, a2),
            pygame.Rect(shadow_pad, sy, draw_rect.width, draw_rect.height),
            border_radius=radius,
        )
        surface.blit(shadow_surf, (draw_rect.x - shadow_pad, draw_rect.y - shadow_pad))

        # Card body
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=radius)
        pygame.draw.rect(surface, border_color, draw_rect, width=border_width, border_radius=radius)

        text_surf = font.render(self.symbol, True, text_color)
        if scale > 1.001:
            scaled_tw = max(1, int(round(text_surf.get_width() * scale)))
            scaled_th = max(1, int(round(text_surf.get_height() * scale)))
            text_surf = pygame.transform.smoothscale(text_surf, (scaled_tw, scaled_th))

        text_x = draw_rect.centerx - text_surf.get_width() // 2
        if cap_offset is not None:
            text_y = int(draw_rect.centery - cap_offset * scale)
        else:
            text_y = draw_rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))
