from typing import Literal
import pygame

from src.config import (
    ALL_LOWERCASE,
    ALL_NUMBERS,
    ALL_UPPERCASE,
    GameConfig,
    MIN_SELECTED_SYMBOLS,
    save_config,
)
from src.font_manager import FontManager
from src.ui_elements import UICheckbox, UIIconButton, draw_progress_circles

ScreenAction = Literal["MENU", "PLAY", "CONFIG", "SCORE", "QUIT"]


class MainMenuScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        center_x = screen_w // 2
        center_y = screen_h // 2

        play_sz = max(110, int(180 * self.scale))
        sub_sz = max(60, int(90 * self.scale))
        sub_gap = max(30, int(60 * self.scale))

        self.btn_play = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2, center_y - play_sz // 2 - int(40 * self.scale), play_sz, play_sz),
            icon_type="PLAY",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            icon_color=(255, 255, 255),
            border_radius=max(20, int(play_sz * 0.22)),
        )

        sub_y = center_y + int(90 * self.scale)
        self.btn_config = UIIconButton(
            rect=pygame.Rect(center_x - sub_sz - sub_gap // 2, sub_y, sub_sz, sub_sz),
            icon_type="GEAR",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(14, int(sub_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )

        self.btn_quit = UIIconButton(
            rect=pygame.Rect(center_x + sub_gap // 2, sub_y, sub_sz, sub_sz),
            icon_type="EXIT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(14, int(sub_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_play.is_clicked(pos):
                return "PLAY"
            if self.btn_config.is_clicked(pos):
                return "CONFIG"
            if self.btn_quit.is_clicked(pos):
                return "QUIT"
        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))
        self.btn_play.render(surface, mouse_pos)
        self.btn_config.render(surface, mouse_pos)
        self.btn_quit.render(surface, mouse_pos)


class ConfigScreen:
    def __init__(self, screen_w: int, screen_h: int, config: GameConfig) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        self.config: GameConfig = config
        self.checkboxes: list[UICheckbox] = []
        self._build_grid()

        btn_sz = max(44, int(64 * self.scale))
        self.btn_back = UIIconButton(
            rect=pygame.Rect(int(40 * self.scale), int(35 * self.scale), btn_sz, btn_sz),
            icon_type="ARROW_LEFT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(btn_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=2,
        )

    def _build_grid(self) -> None:
        self.checkboxes.clear()
        selected_set = set(self.config.selected_symbols)
        box_w = max(28, int(46 * self.scale))
        box_h = max(28, int(46 * self.scale))
        pad = max(4, int(8 * self.scale))

        def add_row(symbols: list[str], start_y: int) -> None:
            cols = len(symbols)
            total_w = cols * (box_w + pad)
            start_x = (self.w - total_w) // 2
            for i, sym in enumerate(symbols):
                r = pygame.Rect(start_x + i * (box_w + pad), start_y, box_w, box_h)
                self.checkboxes.append(UICheckbox(r, sym, checked=(sym in selected_set)))

        add_row(ALL_UPPERCASE, self.h // 2 - int(150 * self.scale))
        add_row(ALL_LOWERCASE, self.h // 2 - int(50 * self.scale))
        add_row(ALL_NUMBERS, self.h // 2 + int(50 * self.scale))

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_back.is_clicked(pos):
                return "MENU"

            for box in self.checkboxes:
                if box.is_clicked(pos):
                    # Enforce minimum active symbols
                    currently_checked = [b.label for b in self.checkboxes if b.checked]
                    if box.checked and len(currently_checked) <= MIN_SELECTED_SYMBOLS:
                        return None

                    box.toggle()
                    # Autosave immediately
                    self.config.selected_symbols = [b.label for b in self.checkboxes if b.checked]
                    save_config(self.config)
                    return None

        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))
        self.btn_back.render(surface, mouse_pos)

        box_font = fm.get_font("Segoe UI", max(14, int(22 * self.scale)), bold=True)
        for box in self.checkboxes:
            box.render(surface, box_font, mouse_pos)


class ScoreScreen:
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        score: int,
        round_results: list[bool] | None = None,
        max_score: int = 10,
    ) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        self.score: int = score
        self.round_results: list[bool] = round_results or []
        self.max_score: int = max_score

        play_sz = max(90, int(150 * self.scale))
        btn_sz = max(50, int(80 * self.scale))
        center_x = screen_w // 2
        center_y = screen_h // 2

        self.btn_replay = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2, center_y + int(110 * self.scale), play_sz, play_sz),
            icon_type="PLAY",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            icon_color=(255, 255, 255),
            border_radius=max(18, int(play_sz * 0.22)),
        )

        self.btn_home = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2 - btn_sz - int(30 * self.scale), center_y + int(145 * self.scale), btn_sz, btn_sz),
            icon_type="ARROW_LEFT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(btn_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_replay.is_clicked(pos):
                return "PLAY"
            if self.btn_home.is_clicked(pos):
                return "MENU"
        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))

        # 10 progress circles on top
        circ_rad = max(10, int(18 * self.scale))
        circ_spacing = max(26, int(52 * self.scale))
        circ_y = self.h // 2 - int(170 * self.scale)
        draw_progress_circles(
            surface=surface,
            center_pos=(self.w // 2, circ_y),
            round_results=self.round_results,
            total_rounds=self.max_score,
            radius=circ_rad,
            spacing=circ_spacing,
        )

        # Bold score number
        score_font = fm.get_font("Segoe UI", max(48, int(120 * self.scale)), bold=True)
        score_surf = score_font.render(f"{self.score}", True, (20, 20, 25))
        score_rect = score_surf.get_rect(center=(self.w // 2, self.h // 2 - int(25 * self.scale)))
        surface.blit(score_surf, score_rect)

        self.btn_replay.render(surface, mouse_pos)
        self.btn_home.render(surface, mouse_pos)
