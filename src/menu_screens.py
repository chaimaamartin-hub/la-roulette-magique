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
from src.ui_elements import UIButton, UICheckbox, draw_star

ScreenAction = Literal["MENU", "PLAY", "CONFIG", "SCORE", "QUIT"]


class MainMenuScreen:
    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        center_x = screen_w // 2

        pw, ph = int(380 * self.scale), int(84 * self.scale)
        cw, ch = int(380 * self.scale), int(74 * self.scale)
        qw, qh = int(240 * self.scale), int(56 * self.scale)

        self.btn_play = UIButton(
            rect=pygame.Rect(center_x - pw // 2, screen_h // 2 - int(30 * self.scale), pw, ph),
            text="Jouer",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            text_color=(255, 255, 255),
            border_radius=int(22 * self.scale),
        )
        self.btn_config = UIButton(
            rect=pygame.Rect(center_x - cw // 2, screen_h // 2 + int(76 * self.scale), cw, ch),
            text="Configuration",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            text_color=(20, 20, 25),
            border_radius=int(20 * self.scale),
            border_color=(20, 20, 25),
            border_width=2,
        )
        self.btn_quit = UIButton(
            rect=pygame.Rect(center_x - qw // 2, screen_h // 2 + int(172 * self.scale), qw, qh),
            text="Quitter",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            text_color=(70, 70, 80),
            border_radius=int(16 * self.scale),
            border_color=(180, 180, 190),
            border_width=1,
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
        title_font = fm.get_font("Segoe UI", max(28, int(56 * self.scale)), bold=True)
        title_surf = title_font.render("Apprenons les Lettres et les Chiffres !", True, (20, 20, 25))
        surface.blit(title_surf, title_surf.get_rect(center=(self.w // 2, self.h // 2 - int(140 * self.scale))))

        self.btn_play.render(surface, fm.get_font("Segoe UI", max(20, int(34 * self.scale)), bold=True), mouse_pos)
        self.btn_config.render(surface, fm.get_font("Segoe UI", max(18, int(26 * self.scale)), bold=True), mouse_pos)
        self.btn_quit.render(surface, fm.get_font("Segoe UI", max(16, int(22 * self.scale)), bold=False), mouse_pos)


class ConfigScreen:
    def __init__(self, screen_w: int, screen_h: int, config: GameConfig) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        self.config: GameConfig = config
        self.checkboxes: list[UICheckbox] = []
        self.error_msg: str | None = None
        self._build_grid()

        sw, sh = int(420 * self.scale), int(68 * self.scale)
        bw, bh = int(160 * self.scale), int(48 * self.scale)
        self.btn_save = UIButton(
            rect=pygame.Rect(screen_w // 2 - sw // 2, screen_h - int(115 * self.scale), sw, sh),
            text="Sauvegarder & Jouer",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            text_color=(255, 255, 255),
            border_radius=int(18 * self.scale),
        )
        self.btn_back = UIButton(
            rect=pygame.Rect(int(40 * self.scale), int(35 * self.scale), bw, bh),
            text="< Retour",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            text_color=(20, 20, 25),
            border_radius=int(14 * self.scale),
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

        add_row(ALL_UPPERCASE, self.h // 2 - int(180 * self.scale))
        add_row(ALL_LOWERCASE, self.h // 2 - int(80 * self.scale))
        add_row(ALL_NUMBERS, self.h // 2 + int(20 * self.scale))

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_back.is_clicked(pos):
                return "MENU"
            for box in self.checkboxes:
                if box.is_clicked(pos):
                    box.toggle()
                    self.error_msg = None
                    return None
            if self.btn_save.is_clicked(pos):
                active = [b.label for b in self.checkboxes if b.checked]
                if len(active) < MIN_SELECTED_SYMBOLS:
                    self.error_msg = f"Veuillez choisir au moins {MIN_SELECTED_SYMBOLS} symboles !"
                    return None
                self.config.selected_symbols = active
                save_config(self.config)
                return "PLAY"
        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))
        title_font = fm.get_font("Segoe UI", max(22, int(42 * self.scale)), bold=True)
        title = title_font.render("Configuration des Symboles", True, (20, 20, 25))
        surface.blit(title, title.get_rect(center=(self.w // 2, int(65 * self.scale))))

        lbl_font = fm.get_font("Segoe UI", max(16, int(22 * self.scale)), bold=True)
        for text, y in [
            ("Lettres Majuscules (A - Z)", self.h // 2 - int(215 * self.scale)),
            ("Lettres Minuscules (a - z)", self.h // 2 - int(115 * self.scale)),
            ("Chiffres (1 - 20)", self.h // 2 - int(15 * self.scale)),
        ]:
            surf = lbl_font.render(text, True, (40, 40, 50))
            surface.blit(surf, (self.w // 2 - surf.get_width() // 2, y))

        box_font = fm.get_font("Segoe UI", max(14, int(22 * self.scale)), bold=True)
        for box in self.checkboxes:
            box.render(surface, box_font, mouse_pos)

        if self.error_msg:
            err_font = fm.get_font("Segoe UI", max(16, int(22 * self.scale)), bold=True)
            err_surf = err_font.render(self.error_msg, True, (20, 20, 25))
            surface.blit(err_surf, err_surf.get_rect(center=(self.w // 2, self.h - int(150 * self.scale))))

        self.btn_save.render(surface, fm.get_font("Segoe UI", max(18, int(26 * self.scale)), bold=True), mouse_pos)
        self.btn_back.render(surface, fm.get_font("Segoe UI", max(16, int(20 * self.scale)), bold=True), mouse_pos)


class ScoreScreen:
    def __init__(self, screen_w: int, screen_h: int, score: int, max_score: int = 10) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        self.score: int = score
        self.max_score: int = max_score

        rw, rh = int(360 * self.scale), int(76 * self.scale)
        hw, hh = int(320 * self.scale), int(64 * self.scale)
        self.btn_replay = UIButton(
            rect=pygame.Rect(screen_w // 2 - rw // 2, screen_h // 2 + int(110 * self.scale), rw, rh),
            text="Rejouer",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            text_color=(255, 255, 255),
            border_radius=int(22 * self.scale),
        )
        self.btn_home = UIButton(
            rect=pygame.Rect(screen_w // 2 - hw // 2, screen_h // 2 + int(205 * self.scale), hw, hh),
            text="Menu Principal",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            text_color=(20, 20, 25),
            border_radius=int(18 * self.scale),
            border_color=(20, 20, 25),
            border_width=2,
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
        title_font = fm.get_font("Segoe UI", max(32, int(64 * self.scale)), bold=True)
        title = title_font.render("Bravo !", True, (20, 20, 25))
        surface.blit(title, title.get_rect(center=(self.w // 2, self.h // 2 - int(160 * self.scale))))

        score_font = fm.get_font("Segoe UI", max(24, int(44 * self.scale)), bold=True)
        score_surf = score_font.render(f"Ton score : {self.score} / {self.max_score}", True, (20, 20, 25))
        surface.blit(score_surf, score_surf.get_rect(center=(self.w // 2, self.h // 2 - int(80 * self.scale))))

        stars = 3 if self.score >= 8 else (2 if self.score >= 5 else (1 if self.score >= 1 else 0))
        star_y = self.h // 2 + int(10 * self.scale)
        spacing = int(100 * self.scale)
        star_rad = max(18, int(36 * self.scale))
        for i in range(3):
            cx = self.w // 2 + (i - 1) * spacing
            draw_star(surface, (cx, star_y), radius=star_rad, filled=(i < stars))

        self.btn_replay.render(surface, fm.get_font("Segoe UI", max(20, int(32 * self.scale)), bold=True), mouse_pos)
        self.btn_home.render(surface, fm.get_font("Segoe UI", max(18, int(26 * self.scale)), bold=True), mouse_pos)
