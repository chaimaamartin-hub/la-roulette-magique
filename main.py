import argparse
import ctypes
import os
from pathlib import Path
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
from src.ui_icons import init_hand_cursor

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


def get_app_icon_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent
    return base / "assets" / "images" / "icons" / "app_icon.png"


def run_app(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    pygame.init()
    pygame.font.init()

    # Set application icon if available
    icon_path = get_app_icon_path()
    if icon_path.is_file():
        try:
            icon_surf = pygame.image.load(str(icon_path))
            pygame.display.set_icon(icon_surf)
        except Exception:
            pass

    if not args.windowed:
        info = pygame.display.Info()
        win_w = info.current_w if info.current_w > 0 else args.width
        win_h = info.current_h if info.current_h > 0 else args.height
        screen = pygame.display.set_mode((win_w, win_h), pygame.FULLSCREEN)
    else:
        win_w, win_h = args.width, args.height
        screen = pygame.display.set_mode((win_w, win_h))

    pygame.display.set_caption("Les Cartes Magiques")
    init_hand_cursor()

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
                if score_screen is not None:
                    score_screen.close()
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
                if score_screen is not None:
                    score_screen.close()
                running = False
                break
            elif action == "MENU":
                if score_screen is not None:
                    score_screen.close()
                am.stop_all()
                current_state = "MENU"
            elif action == "CONFIG":
                if score_screen is not None:
                    score_screen.close()
                config_screen = ConfigScreen(win_w, win_h, config)
                current_state = "CONFIG"
            elif action == "PLAY":
                if score_screen is not None:
                    score_screen.close()
                am.stop_all()
                session = GameSession(
                    symbol_pool=config.selected_symbols,
                    ask_letter_names=config.ask_letter_names,
                    ask_letter_sounds=config.ask_letter_sounds,
                )
                game_screen = GameScreen(win_w, win_h, session, am)
                current_state = "PLAY"
            elif action == "SCORE" and game_screen is not None:
                score_screen = ScoreScreen(
                    win_w,
                    win_h,
                    game_screen.session.score,
                    round_results=game_screen.session.round_results,
                    audio_mgr=am,
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
                    audio_mgr=am,
                )
                current_state = "SCORE"
        elif current_state == "SCORE" and score_screen is not None:
            score_screen.update(dt)

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
