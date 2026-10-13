from typing import Literal
import pygame

from src.audio_manager import AudioManager
from src.card import Card
from src.font_manager import FontManager
from src.game_state import GameSession
from src.ui_elements import UIIconButton, draw_progress_stars

GamePhase = Literal["FLYING_IN", "WAITING_GUESS", "SOLVED_FEEDBACK", "FLYING_OUT"]


class GameScreen:
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        session: GameSession,
        audio_manager: AudioManager,
    ) -> None:
        self.w: int = screen_w
        self.h: int = screen_h
        self.session: GameSession = session
        self.am: AudioManager = audio_manager

        self.cards: list[Card] = []
        self.phase: GamePhase = "FLYING_IN"
        self.phase_time: float = 0.0
        self.has_played_question: bool = False

        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        btn_sz = max(44, int(64 * self.scale))
        self.btn_menu = UIIconButton(
            rect=pygame.Rect(int(40 * self.scale), int(30 * self.scale), btn_sz, btn_sz),
            icon_type="ARROW_LEFT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(btn_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=2,
        )

        self._setup_round()

    def _setup_round(self) -> None:
        self.cards.clear()
        self.phase = "FLYING_IN"
        self.phase_time = 0.0
        self.has_played_question = False

        round_data = self.session.current_round
        self.am.set_voice(round_data.voice_type)

        symbols = round_data.displayed_symbols
        n = len(symbols)

        base_w = 210 if n <= 4 else 180
        base_h = 290 if n <= 4 else 260
        base_spacing = 36 if n <= 4 else 24

        card_w = max(80, int(base_w * self.scale))
        card_h = max(100, int(base_h * self.scale))
        spacing = max(12, int(base_spacing * self.scale))

        total_w = n * card_w + (n - 1) * spacing
        start_x = (self.w - total_w) // 2
        card_y = (self.h - card_h) // 2 + int(30 * self.scale)

        for i, sym in enumerate(symbols):
            r = pygame.Rect(start_x + i * (card_w + spacing), card_y, card_w, card_h)
            self.cards.append(
                Card(symbol=sym, index=i, target_rect=r, screen_width=self.w, entry_delay=0.08)
            )

    def handle_event(self, event: pygame.event.Event) -> Literal["MENU", "SCORE"] | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.btn_menu.is_clicked(pos):
                self.am.stop_all()
                return "MENU"

            if self.phase == "WAITING_GUESS":
                for card in self.cards:
                    if card.is_clicked(pos):
                        self._handle_card_click(card)
                        break

        return None

    def _handle_card_click(self, card: Card) -> None:
        is_correct = self.session.process_guess(card.symbol)
        if is_correct:
            self.am.play_sfx_correct()
            card.trigger_rainbow()
            self.am.play_voice(card.symbol, "ans_pos")
            self.phase = "SOLVED_FEEDBACK"
            self.phase_time = 0.0
        else:
            self.am.play_sfx_wrong()
            card.trigger_red_flash()
            self.am.play_voice(card.symbol, "ans_neg")

    def update(self, dt: float) -> Literal["SCORE"] | None:
        self.phase_time += dt

        for card in self.cards:
            card.update(dt)

        if self.phase == "FLYING_IN":
            if not self.has_played_question and self.phase_time >= 0.2:
                self.am.play_voice(self.session.current_round.target_symbol, "question")
                self.has_played_question = True

            all_idle = all(c.state == "IDLE" for c in self.cards)
            if all_idle and self.phase_time >= 0.6:
                self.phase = "WAITING_GUESS"
                self.phase_time = 0.0

        elif self.phase == "SOLVED_FEEDBACK":
            # Wait until celebration sound and rainbow finish
            if not self.am.is_voice_busy() and self.phase_time >= 0.9:
                for c in self.cards:
                    c.trigger_fly_out()
                self.phase = "FLYING_OUT"
                self.phase_time = 0.0

        elif self.phase == "FLYING_OUT":
            if self.phase_time >= 0.8:
                if self.session.advance_to_next_round():
                    self._setup_round()
                else:
                    return "SCORE"

        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))

        self.btn_menu.render(surface, mouse_pos)

        # 10 progress stars on top center (no text)
        circ_rad = max(8, int(15 * self.scale))
        circ_spacing = max(22, int(46 * self.scale))
        draw_progress_stars(
            surface=surface,
            center_pos=(self.w // 2, int(45 * self.scale)),
            round_results=self.session.round_results,
            total_rounds=10,
            radius=circ_rad,
            spacing=circ_spacing,
            filled_color=(235, 165, 0),
        )

        base_font_size = 110 if len(self.cards) <= 4 else 95
        card_font_size = max(28, int(base_font_size * self.scale))
        round_font = fm.get_round_font(self.session.current_round_num, card_font_size)
        cap_offset = fm.get_cap_center_offset(round_font)

        for card in self.cards:
            card.render(surface, round_font, cap_offset=cap_offset)
