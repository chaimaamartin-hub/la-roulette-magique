import math
from typing import Callable
import pygame


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
        color = self.hover_color if hover else self.bg_color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        if self.border_color is not None and self.border_width > 0:
            pygame.draw.rect(
                surface,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_radius,
            )

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


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
        hover = self.rect.collidepoint(mouse_pos)
        if self.checked:
            bg = (20, 20, 25)
            border = (20, 20, 25)
            text_color = (255, 255, 255)
        else:
            bg = (240, 240, 245) if hover else (255, 255, 255)
            border = (140, 140, 150)
            text_color = (20, 20, 25)

        radius = max(6, self.rect.width // 4)
        pygame.draw.rect(surface, bg, self.rect, border_radius=radius)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=radius)

        text_surf = font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


def draw_star(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    filled: bool,
    color: tuple[int, int, int] = (255, 204, 0),
) -> None:
    cx, cy = center
    points: list[tuple[float, float]] = []
    inner_radius = radius * 0.42

    for i in range(10):
        r = radius if i % 2 == 0 else inner_radius
        angle = math.pi / 2 + i * (math.pi / 5)
        px = cx + r * math.cos(angle)
        py = cy - r * math.sin(angle)
        points.append((px, py))

    if filled:
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (218, 165, 32), points, width=3)
    else:
        pygame.draw.polygon(surface, (220, 220, 225), points)
        pygame.draw.polygon(surface, (180, 180, 190), points, width=3)
