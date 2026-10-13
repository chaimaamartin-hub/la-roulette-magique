import argparse
import ctypes
import os
import sys
from typing import Literal
import pygame

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

os.environ["SDL_RENDER_SCALE_QUALITY"] = "2"

from src.audio_manager import AudioManager
from src.config import GameConfig, load_config
from src.font_manager import FontManager
from src.game_screen import GameScreen
from src.game_state import GameSession
from src.menu_screens import ConfigScreen, MainMenuScreen, ScoreScreen

SCREEN_WIDTH: int = 1920
SCREEN_HEIGHT: int = 1080
FPS: int = 60

CurrentState = Literal["MENU", "CONFIG", "PLAY", "SCORE"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="La Roulette Magique - French Learner Game")
    parser.add_argument("--windowed", action="store_true", help="Launch in a window instead of fullscreen.")
    parser.add_argument("--width", type=int, default=SCREEN_WIDTH, help="Screen width (default: 1920).")
    parser.add_argument("--height", type=int, default=SCREEN_HEIGHT, help="Screen height (default: 1080).")
    return parser.parse_args(argv)


def run_app(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    pygame.init()
    pygame.font.init()

    if not args.windowed:
        info = pygame.display.Info()
        win_w = info.current_w if info.current_w > 0 else args.width
        win_h = info.current_h if info.current_h > 0 else args.height
        screen = pygame.display.set_mode((win_w, win_h), pygame.FULLSCREEN)
    else:
        win_w, win_h = args.width, args.height
        screen = pygame.display.set_mode((win_w, win_h))

    pygame.display.set_caption("La Roulette Magique")

    clock = pygame.time.Clock()
    fm = FontManager()
    am = AudioManager()
    config: GameConfig = load_config()

    current_state: CurrentState = "MENU"
    menu_screen = MainMenuScreen(win_w, win_h)
    config_screen = ConfigScreen(win_w, win_h, config)
    game_screen: GameScreen | None = None
    score_screen: ScoreScreen | None = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if current_state == "MENU":
                    running = False
                    break
                am.stop_all()
                current_state = "MENU"
                continue

            # Route events to active screen
            action = None
            if current_state == "MENU":
                action = menu_screen.handle_event(event)
            elif current_state == "CONFIG":
                action = config_screen.handle_event(event)
            elif current_state == "PLAY" and game_screen is not None:
                action = game_screen.handle_event(event)
            elif current_state == "SCORE" and score_screen is not None:
                action = score_screen.handle_event(event)

            if action == "QUIT":
                running = False
                break
            elif action == "MENU":
                am.stop_all()
                current_state = "MENU"
            elif action == "CONFIG":
                config_screen = ConfigScreen(win_w, win_h, config)
                current_state = "CONFIG"
            elif action == "PLAY":
                am.stop_all()
                session = GameSession(config.selected_symbols)
                game_screen = GameScreen(win_w, win_h, session, am)
                current_state = "PLAY"
            elif action == "SCORE" and game_screen is not None:
                score_screen = ScoreScreen(
                    win_w,
                    win_h,
                    game_screen.session.score,
                    round_results=game_screen.session.round_results,
                )
                current_state = "SCORE"

        # Update active screen
        if current_state == "PLAY" and game_screen is not None:
            play_res = game_screen.update(dt)
            if play_res == "SCORE":
                score_screen = ScoreScreen(
                    win_w,
                    win_h,
                    game_screen.session.score,
                    round_results=game_screen.session.round_results,
                )
                current_state = "SCORE"

        # Render active screen
        if current_state == "MENU":
            menu_screen.render(screen, fm, mouse_pos)
        elif current_state == "CONFIG":
            config_screen.render(screen, fm, mouse_pos)
        elif current_state == "PLAY" and game_screen is not None:
            game_screen.render(screen, fm, mouse_pos)
        elif current_state == "SCORE" and score_screen is not None:
            score_screen.render(screen, fm, mouse_pos)

        pygame.display.flip()

    am.stop_all()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(run_app())
