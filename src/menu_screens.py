from typing import Literal
import pygame

from src.animal_manager import AnimalManager
from src.audio_manager import AudioManager
from src.config import (
    ALL_LOWERCASE,
    ALL_NUMBERS,
    ALL_UPPERCASE,
    GameConfig,
    MIN_SELECTED_SYMBOLS,
    save_config,
)
from src.font_manager import FontManager
from src.ui_elements import UICheckbox, UIIconButton, draw_progress_stars

ScreenAction = Literal["MENU", "PLAY", "CONFIG", "SCORE", "QUIT"]


class MainMenuScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        center_x = screen_w // 2
        center_y = screen_h // 2

        play_sz = max(90, int(130 * self.scale))
        sub_sz = max(55, int(80 * self.scale))

        # Three vertically aligned buttons
        self.btn_play = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2, center_y - int(45 * self.scale), play_sz, play_sz),
            icon_type="PLAY",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            icon_color=(255, 255, 255),
            border_radius=max(18, int(play_sz * 0.22)),
        )

        self.btn_config = UIIconButton(
            rect=pygame.Rect(center_x - sub_sz // 2, center_y + int(110 * self.scale), sub_sz, sub_sz),
            icon_type="GEAR",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(sub_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )

        self.btn_quit = UIIconButton(
            rect=pygame.Rect(center_x - sub_sz // 2, center_y + int(210 * self.scale), sub_sz, sub_sz),
            icon_type="EXIT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(sub_sz * 0.22)),
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

        # Title: LES CARTES MAGIQUES (enlarged by 20%)
        title_font = fm.get_title_font(max(44, int(77 * self.scale)))
        title_surf = title_font.render("LES CARTES MAGIQUES", True, (20, 20, 25))
        title_rect = title_surf.get_rect(center=(self.w // 2, self.h // 2 - int(160 * self.scale)))
        surface.blit(title_surf, title_rect)

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

        mode_w = max(170, int(240 * self.scale))
        mode_h = max(34, int(46 * self.scale))
        mode_spacing = max(16, int(24 * self.scale))
        total_mode_w = mode_w * 2 + mode_spacing
        start_mode_x = (self.w - total_mode_w) // 2
        mode_y = self.h // 2 + int(140 * self.scale)

        self.btn_mode_names = UICheckbox(
            rect=pygame.Rect(start_mode_x, mode_y, mode_w, mode_h),
            label="Nom des lettres",
            checked=self.config.ask_letter_names,
        )
        self.btn_mode_sounds = UICheckbox(
            rect=pygame.Rect(start_mode_x + mode_w + mode_spacing, mode_y, mode_w, mode_h),
            label="Son des lettres",
            checked=self.config.ask_letter_sounds,
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

            if self.btn_mode_names.is_clicked(pos):
                if self.btn_mode_names.checked and not self.btn_mode_sounds.checked:
                    return None
                self.btn_mode_names.toggle()
                self.config.ask_letter_names = self.btn_mode_names.checked
                save_config(self.config)
                return None

            if self.btn_mode_sounds.is_clicked(pos):
                if self.btn_mode_sounds.checked and not self.btn_mode_names.checked:
                    return None
                self.btn_mode_sounds.toggle()
                self.config.ask_letter_sounds = self.btn_mode_sounds.checked
                save_config(self.config)
                return None

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

        mode_font = fm.get_font("Segoe UI", max(13, int(20 * self.scale)), bold=True)
        self.btn_mode_names.render(surface, mode_font, mouse_pos)
        self.btn_mode_sounds.render(surface, mode_font, mouse_pos)


from src.score_screen import ScoreScreen

