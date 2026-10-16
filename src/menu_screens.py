import math
import time
from typing import Literal
import pygame

from src.animal_manager import AnimalManager
from src.audio_manager import AudioManager
from src.card import sample_rainbow_band_color
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


def render_title_shimmer(title_mask: pygame.Surface, anim_t: float) -> pygame.Surface:
    if not isinstance(anim_t, (int, float)) or math.isnan(anim_t):
        raise ValueError("CRITICAL: anim_t must be a valid number.")
    w, h = title_mask.get_size()
    if w <= 0 or h <= 0:
        raise ValueError("CRITICAL: title_mask dimensions must be positive.")

    shimmer_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    shimmer_surf.fill((20, 20, 25, 255))

    # Periodic diagonal 12-color rainbow wave gliding across the title
    cycle = 4.5
    prog = (anim_t % cycle) / cycle
    sweep_span = w + h + 280
    center_u = prog * (sweep_span + 280) - 140
    band_w = max(24.0, h * 0.45)

    u_start = max(0, int(center_u - 160))
    u_end = min(w + h, int(center_u + 160))
    for u in range(u_start, u_end):
        dist = abs(u - center_u) / 160.0
        if dist < 1.0:
            blend = 0.5 * (1.0 + math.cos(dist * math.pi))
            r, g, b = sample_rainbow_band_color((u / band_w) - anim_t * 2.5, 0.85, 0.92, 0.35)
            col = (
                int(round(20 + (r - 20) * blend)),
                int(round(20 + (g - 20) * blend)),
                int(round(25 + (b - 25) * blend)),
                255,
            )
            pygame.draw.line(shimmer_surf, col, (u, 0), (0, u), 2)

    shimmer_surf.blit(title_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return shimmer_surf


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
        self._cached_title_surf: pygame.Surface | None = None
        self._cached_title_scale: float = 0.0

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

        # Title: LES CARTES MAGIQUES with 2x supersampled anti-aliasing + diagonal rainbow shimmer
        if self._cached_title_surf is None or self._cached_title_scale != self.scale:
            base_sz = max(44, int(77 * self.scale))
            title_font_2x = fm.get_title_font(base_sz * 2)
            raw_title = title_font_2x.render("LES CARTES MAGIQUES", True, (255, 255, 255))
            target_w = max(1, raw_title.get_width() // 2)
            target_h = max(1, raw_title.get_height() // 2)
            self._cached_title_surf = pygame.transform.smoothscale(raw_title, (target_w, target_h))
            self._cached_title_scale = self.scale

        shimmer_title = render_title_shimmer(self._cached_title_surf, time.time())
        title_rect = shimmer_title.get_rect(
            center=(self.w // 2, self.h // 2 - int(160 * self.scale))
        )
        surface.blit(shimmer_title, title_rect)

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

        self.error_message: str = ""
        self.error_hide_time: float = 0.0

    def show_error(self, message: str, duration: float = 2.5) -> None:
        self.error_message = message
        self.error_hide_time = time.time() + duration

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
                    self.show_error("Choisis au moins un mode de jeu !")
                    return None
                self.btn_mode_names.toggle()
                self.config.ask_letter_names = self.btn_mode_names.checked
                save_config(self.config)
                return None

            if self.btn_mode_sounds.is_clicked(pos):
                if self.btn_mode_sounds.checked and not self.btn_mode_names.checked:
                    self.show_error("Choisis au moins un mode de jeu !")
                    return None
                self.btn_mode_sounds.toggle()
                self.config.ask_letter_sounds = self.btn_mode_sounds.checked
                save_config(self.config)
                return None

            for box in self.checkboxes:
                if box.is_clicked(pos):
                    # Enforce minimum active distinct case-insensitive symbols
                    if box.checked:
                        remaining_distinct = {
                            b.label.upper() for b in self.checkboxes if b.checked and b is not box
                        }
                        if len(remaining_distinct) < MIN_SELECTED_SYMBOLS:
                            self.show_error(f"Choisis au moins {MIN_SELECTED_SYMBOLS} lettres ou chiffres !")
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

        now = time.time()
        if now < self.error_hide_time and self.error_message:
            rem = self.error_hide_time - now
            alpha = min(255, int(255 * (rem / 0.4))) if rem < 0.4 else 255
            err_font = fm.get_font("Segoe UI", max(14, int(20 * self.scale)), bold=True)
            txt_surf = err_font.render(self.error_message, True, (215, 45, 45))
            if alpha < 255:
                txt_surf.set_alpha(alpha)
            txt_rect = txt_surf.get_rect(center=(self.w // 2, self.h // 2 + int(215 * self.scale)))
            surface.blit(txt_surf, txt_rect)


from src.score_screen import ScoreScreen

