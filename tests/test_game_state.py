from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.game_state import (
    GameSession,
    get_symbol_count_for_round,
    TOTAL_ROUNDS,
)


def test_symbol_counts_progression() -> None:
    assert get_symbol_count_for_round(1) == 3
    assert get_symbol_count_for_round(4) == 3
    assert get_symbol_count_for_round(5) == 4
    assert get_symbol_count_for_round(7) == 4
    assert get_symbol_count_for_round(8) == 5
    assert get_symbol_count_for_round(10) == 5


def test_symbol_count_invalid_round() -> None:
    with pytest.raises(ValueError, match="CRITICAL: round_number must be 1..10"):
        get_symbol_count_for_round(0)

    with pytest.raises(ValueError, match="CRITICAL: round_number must be 1..10"):
        get_symbol_count_for_round(11)


def test_session_init_too_few_symbols() -> None:
    with pytest.raises(ValueError, match="CRITICAL: symbol_pool must have at least 5 symbols"):
        GameSession(["A", "B", "C"])


def test_game_session_progression_and_scoring() -> None:
    pool = ["A", "B", "C", "D", "E", "F", "G"]
    session = GameSession(pool)

    assert session.current_round_num == 1
    assert len(session.current_round.displayed_symbols) == 3
    assert session.current_round.target_symbol in session.current_round.displayed_symbols
    assert len(set(session.current_round.displayed_symbols)) == 3

    # Round 1: Wrong guess first, then correct guess -> score should be 0
    target = session.current_round.target_symbol
    wrong = [s for s in session.current_round.displayed_symbols if s != target][0]

    assert not session.process_guess(wrong)
    assert session.current_round.attempts == 1
    assert not session.current_round.first_attempt_success

    assert session.process_guess(target)
    assert session.current_round.is_solved
    assert session.score == 0  # No point awarded because of initial wrong guess

    # Advance to Round 2
    assert session.advance_to_next_round()
    assert session.current_round_num == 2
    assert session.round_results == [False]  # First round failed initial attempt

    # Round 2: Correct guess on first attempt -> score +1
    target2 = session.current_round.target_symbol
    assert session.process_guess(target2)
    assert session.score == 1
    assert session.advance_to_next_round()
    assert session.round_results == [False, True]


def test_cannot_advance_unsolved_round() -> None:
    pool = ["A", "B", "C", "D", "E"]
    session = GameSession(pool)
    with pytest.raises(RuntimeError, match="CRITICAL: Cannot advance round before target is solved"):
        session.advance_to_next_round()
