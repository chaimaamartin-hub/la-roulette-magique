import colorsys
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
        self.state_time: float = 0.0
        self.fly_in_duration: float = 0.5
        self.fly_out_duration: float = 0.5
        self.rainbow_duration: float = 0.8
        self.red_flash_duration: float = 0.4

    def update(self, dt: float) -> None:
        self.state_time += dt

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
        self.state = "RAINBOW_FLASH"
        self.state_time = 0.0

    def trigger_red_flash(self) -> None:
        self.state = "RED_FLASH"
        self.state_time = 0.0

    def trigger_fly_out(self) -> None:
        self.state = "FLYING_OUT"
        self.state_time = 0.0

    def get_current_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.current_x), int(self.current_y), self.width, self.height)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        if self.state not in ("IDLE", "RED_FLASH"):
            return False
        return self.get_current_rect().collidepoint(pos)

    def render(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        cap_offset: float | None = None,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        rect = self.get_current_rect()
        is_hovered = mouse_pos is not None and rect.collidepoint(mouse_pos)
        if is_hovered and self.state in ("IDLE", "FLYING_IN"):
            bg_color = (255, 252, 220)  # Very light yellow hover
            border_color = (220, 210, 160)
        else:
            bg_color = (255, 255, 255)
            border_color = (200, 200, 210)
        border_width = 4
        text_color = (34, 34, 34)

        if self.state == "RED_FLASH":
            factor = 1.0 - (self.state_time / self.red_flash_duration)
            factor = max(0.0, min(1.0, factor))
            r = int(255)
            g = int(255 - (255 - 77) * factor)
            b = int(255 - (255 - 77) * factor)
            bg_color = (r, g, b)
            border_color = (255, 77, 77)
            border_width = 6

        elif self.state == "RAINBOW_FLASH":
            hue = (self.state_time / self.rainbow_duration) % 1.0
            rgb_f = colorsys.hsv_to_rgb(hue, 0.9, 0.95)
            rainbow_col = (int(rgb_f[0] * 255), int(rgb_f[1] * 255), int(rgb_f[2] * 255))
            border_color = rainbow_col
            border_width = 8
            text_color = rainbow_col

        radius = min(28, rect.width // 6)
        pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)

        text_surf = font.render(self.symbol, True, text_color)
        text_x = rect.centerx - text_surf.get_width() // 2
        if cap_offset is not None:
            text_y = int(rect.centery - cap_offset)
        else:
            text_y = rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (text_x, text_y))
