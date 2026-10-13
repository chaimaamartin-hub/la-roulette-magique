from pathlib import Path
import sys
from unittest.mock import MagicMock
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.game_screen import GameScreen
from src.game_state import GameSession


@pytest.fixture(scope="module", autouse=True)
def init_pygame() -> None:
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()


def test_game_screen_setup_and_card_layout() -> None:
    mock_am = MagicMock()
    session = GameSession(["A", "B", "C", "D", "E"])
    screen = GameScreen(1280, 720, session, mock_am)

    assert len(screen.cards) == 3
    assert screen.phase == "FLYING_IN"

    # Finish fly-in
    screen.update(1.0)
    assert screen.phase == "WAITING_GUESS"


def test_game_screen_correct_and_wrong_click() -> None:
    mock_am = MagicMock()
    mock_am.is_voice_busy.return_value = False
    session = GameSession(["A", "B", "C", "D", "E"])
    screen = GameScreen(1280, 720, session, mock_am)
    screen.update(1.0)

    target_sym = session.current_round.target_symbol
    target_card = [c for c in screen.cards if c.symbol == target_sym][0]
    wrong_card = [c for c in screen.cards if c.symbol != target_sym][0]

    # Click wrong card
    screen._handle_card_click(wrong_card)
    assert mock_am.play_sfx_wrong.called
    assert screen.phase == "WAITING_GUESS"  # still waiting for correct guess

    # Click correct card
    screen._handle_card_click(target_card)
    assert mock_am.play_sfx_correct.called
    assert screen.phase == "SOLVED_FEEDBACK"

    # Progress through feedback to fly-out
    screen.update(1.0)
    assert screen.phase == "FLYING_OUT"


def test_game_screen_menu_button() -> None:
    mock_am = MagicMock()
    session = GameSession(["A", "B", "C", "D", "E"])
    screen = GameScreen(1280, 720, session, mock_am)

    ev_menu = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": screen.btn_menu.rect.center})
    assert screen.handle_event(ev_menu) == "MENU"
    assert mock_am.stop_all.called
