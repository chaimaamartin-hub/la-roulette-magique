from typing import Literal
import pygame

from src.animal_manager import AnimalManager, get_score_subtitle
from src.audio_manager import AudioManager
from src.font_manager import FontManager
from src.ui_elements import UIIconButton, draw_progress_stars
from src.video_player import AnimalVideoPlayer

ScreenAction = Literal["MENU", "PLAY", "CONFIG", "SCORE", "QUIT"]


class ScoreScreen:
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        score: int,
        round_results: list[bool] | None = None,
        max_score: int = 10,
        animal_mgr: AnimalManager | None = None,
        audio_mgr: AudioManager | None = None,
        video_preloader: object | None = None,
        video_player: AnimalVideoPlayer | None = None,
    ) -> None:
        if screen_w <= 0 or screen_h <= 0:
            raise ValueError(f"CRITICAL: screen dimensions must be positive, got {screen_w}x{screen_h}")

        self.w: int = screen_w
        self.h: int = screen_h
        self.scale: float = min(screen_w / 1920.0, screen_h / 1080.0)
        self.score: int = min(max(0, score), max_score)
        self.round_results: list[bool] = round_results or []
        self.max_score: int = max_score
        self.animal_mgr: AnimalManager = animal_mgr if animal_mgr is not None else AnimalManager()
        self.audio_mgr: AudioManager | None = audio_mgr

        # Play reward animal sound on screen display
        if self.audio_mgr is not None:
            self.audio_mgr.play_animal_sound(self.score)

        # Animation timer
        self.anim_time: float = 0.0
        self.fade_duration: float = 0.45  # Under 0.5s per spec

        # Center layout
        center_x = screen_w // 2
        center_y = screen_h // 2

        # Animal twice as big as previous (260 -> 520)
        self.animal_sz: int = max(320, int(520 * self.scale))
        self.animal_pos: tuple[int, int] = (center_x, center_y - int(10 * self.scale))

        # Check for animal video (plays with volume 0, seamlessly looping)
        if video_player is not None:
            self.video_player: AnimalVideoPlayer | None = video_player
        elif video_preloader is not None and hasattr(video_preloader, "get_or_create_player"):
            self.video_player = video_preloader.get_or_create_player(self.score, self.animal_sz)
        elif self.animal_mgr.has_video(self.score):
            video_path = self.animal_mgr.get_video_path(self.score)
            if video_path is not None:
                try:
                    self.video_player = AnimalVideoPlayer(
                        video_path=video_path,
                        target_height=self.animal_sz,
                    )
                except Exception:
                    self.video_player = None
        else:
            self.video_player = None

        # Target stars position
        self.circ_rad: int = max(10, int(18 * self.scale))
        self.circ_spacing: int = max(26, int(52 * self.scale))
        self.circ_target_y: int = center_y - int(340 * self.scale)
        self.circ_start_y: int = -int(80 * self.scale)

        # Play button (a bit smaller: was 130 * scale, now 95 * scale)
        play_sz = max(65, int(95 * self.scale))
        btn_y = center_y + int(290 * self.scale)
        self.btn_replay: UIIconButton = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2, btn_y, play_sz, play_sz),
            icon_type="PLAY",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            icon_color=(255, 255, 255),
            border_radius=max(16, int(play_sz * 0.22)),
        )

    def update(self, dt: float) -> None:
        self.anim_time += dt
        if self.video_player is not None:
            self.video_player.update(dt)

    def handle_event(self, event: pygame.event.Event) -> ScreenAction | None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_replay.is_clicked(event.pos):
                return "PLAY"
        return None

    def render(self, surface: pygame.Surface, fm: FontManager, mouse_pos: tuple[int, int]) -> None:
        surface.fill((255, 255, 255))
        center_x = self.w // 2

        # 1. Falling stars animation (drops from above the screen into place over <= 0.45s)
        star_offsets: list[int] = []
        for i in range(self.max_score):
            # Subtle stagger of 0.02s per star
            stagger = i * 0.015
            star_t = min(1.0, max(0.0, (self.anim_time - stagger) / 0.35))
            # Ease-out cubic fall
            eased_fall = 1.0 - ((1.0 - star_t) ** 3)
            current_y = self.circ_start_y + (self.circ_target_y - self.circ_start_y) * eased_fall
            offset_from_target = int(current_y - self.circ_target_y)
            star_offsets.append(offset_from_target)

        draw_progress_stars(
            surface=surface,
            center_pos=(center_x, self.circ_target_y),
            round_results=self.round_results,
            total_rounds=self.max_score,
            radius=self.circ_rad,
            spacing=self.circ_spacing,
            filled_color=(235, 165, 0),
            star_y_offsets=star_offsets,
        )

        # 2. Animal illustration or video (2x size, fades in over <= 0.45s)
        fade_t = min(1.0, max(0.0, self.anim_time / self.fade_duration))
        alpha = int(255 * fade_t)

        if self.video_player is not None:
            animal_surf = self.video_player.get_current_frame()
        else:
            animal_surf = self.animal_mgr.get_animal_surface(self.score, self.animal_sz)

        draw_x = self.animal_pos[0] - animal_surf.get_width() // 2
        draw_y = self.animal_pos[1] - animal_surf.get_height() // 2

        if alpha < 255:
            temp_surf = animal_surf.copy()
            temp_surf.set_alpha(alpha)
            surface.blit(temp_surf, (draw_x, draw_y))
        else:
            surface.blit(animal_surf, (draw_x, draw_y))

        # 3. Play button (quickly fades in over <= 0.4s)
        btn_fade_t = min(1.0, max(0.0, self.anim_time / 0.4))
        btn_alpha = int(255 * btn_fade_t)

        if btn_alpha < 255:
            btn_surf = pygame.Surface(self.btn_replay.rect.size, pygame.SRCALPHA)
            local_mouse = (mouse_pos[0] - self.btn_replay.rect.x, mouse_pos[1] - self.btn_replay.rect.y)
            # Temporarily render at (0, 0) of btn_surf
            orig_rect = self.btn_replay.rect
            self.btn_replay.rect = pygame.Rect(0, 0, orig_rect.width, orig_rect.height)
            self.btn_replay.render(btn_surf, local_mouse)
            self.btn_replay.rect = orig_rect
            btn_surf.set_alpha(btn_alpha)
            surface.blit(btn_surf, orig_rect.topleft)
        else:
            self.btn_replay.render(surface, mouse_pos)

        # 4. Motivational message in small font and very light grey at bottom of screen
        msg_text = get_score_subtitle(self.score)
        msg_font = fm.get_ui_font(max(14, int(20 * self.scale)), bold=False)
        msg_surf = msg_font.render(msg_text, True, (190, 190, 200))
        msg_rect = msg_surf.get_rect(center=(center_x, self.h - int(35 * self.scale)))

        if alpha < 255:
            msg_temp = msg_surf.copy()
            msg_temp.set_alpha(alpha)
            surface.blit(msg_temp, msg_rect)
        else:
            surface.blit(msg_surf, msg_rect)

    def close(self) -> None:
        if getattr(self, "video_player", None) is not None:
            self.video_player.close()
            self.video_player = None

    def __del__(self) -> None:
        self.close()

