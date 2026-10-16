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


def test_no_consecutive_rounds_have_same_target() -> None:
    # Test across multiple sessions to ensure consecutive rounds never repeat target symbol
    pool = ["A", "B", "C", "D", "E", "F"]
    for _ in range(25):
        session = GameSession(pool)
        targets: list[str] = [session.current_round.target_symbol]
        for _ in range(TOTAL_ROUNDS - 1):
            assert session.process_guess(session.current_round.target_symbol)
            assert session.advance_to_next_round()
            targets.append(session.current_round.target_symbol)

        assert len(targets) == TOTAL_ROUNDS
        for i in range(1, len(targets)):
            assert targets[i] != targets[i - 1], f"Repeated target {targets[i]} between round {i} and {i + 1}"


def test_init_round_validation_failure_paths() -> None:
    pool = ["A", "B", "C", "D", "E"]
    session = GameSession(pool)

    # Failure path 1: Invalid round index <= 0 or > TOTAL_ROUNDS
    with pytest.raises(ValueError, match="CRITICAL: round_num must be 1..10"):
        session._init_round(0, None)
    with pytest.raises(ValueError, match="CRITICAL: round_num must be 1..10"):
        session._init_round(11, None)

    # Failure path 2: No available targets after excluding previous target
    session.symbol_pool = ["A"]
    with pytest.raises(ValueError, match="CRITICAL: No available targets after excluding previous target"):
        session._init_round(1, previous_target="A")


def test_phonetic_mode_k_collision_avoidance_happy_path() -> None:
    # Pool with C, K, Q and others
    pool = ["C", "K", "Q", "A", "B", "E", "O", "T"]
    for _ in range(20):
        session = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
        assert session.current_round.prompt_mode == "PHONETIC"
        target = session.current_round.target_symbol
        displayed = session.current_round.displayed_symbols
        assert target in displayed

        # If target is C, K, or Q, the other K-sound letters must NOT be in displayed symbols
        if target in {"C", "K", "Q"}:
            k_letters_in_round = [s for s in displayed if s in {"C", "K", "Q"}]
            assert k_letters_in_round == [target], f"K-sound collision detected: {displayed}"


def test_phonetic_mode_silent_letters_exclusion() -> None:
    # Silent letters (H, W, X) must never be chosen as phonetic targets
    pool = ["H", "W", "X", "A", "B", "1", "2"]
    for _ in range(20):
        session = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
        if session.current_round.prompt_mode == "PHONETIC":
            assert session.current_round.target_symbol not in {"H", "W", "X"}


def test_phonetic_mode_failure_paths() -> None:
    pool = ["A", "B", "C", "D", "E"]

    # Failure path 1: Both prompt modes disabled
    with pytest.raises(ValueError, match="CRITICAL: At least one prompt mode"):
        GameSession(pool, ask_letter_names=False, ask_letter_sounds=False)

    # Failure path 2: Insufficient distractors satisfying phonetic constraints
    k_only_pool = ["C", "K", "Q", "c", "k"]
    with pytest.raises(ValueError, match="CRITICAL: Not enough distractors in pool satisfying phonetic constraints"):
        GameSession(k_only_pool, ask_letter_names=False, ask_letter_sounds=True)


def test_phonetic_mode_includes_numbers() -> None:
    # 1 Happy Path: Numbers and letters are both chosen in letter sound mode
    pool = ["A", "B", "C", "D", "1", "2", "3", "4"]
    number_targets_count = 0
    letter_targets_count = 0

    for _ in range(50):
        session = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
        target = session.current_round.target_symbol
        if target.isdigit():
            number_targets_count += 1
            # Number target must have NAME prompt mode
            assert session.current_round.prompt_mode == "NAME"
        else:
            letter_targets_count += 1
            # Letter target must have PHONETIC prompt mode
            assert session.current_round.prompt_mode == "PHONETIC"

    assert number_targets_count > 0, "Numbers were never selected in phonetic mode!"
    assert letter_targets_count > 0, "Letters were never selected in phonetic mode!"


def test_phonetic_mode_silent_letters_letter_name_fallback() -> None:
    # 1 Happy Path: Silent letters (H, W, X) are selected as targets in sound-only mode
    # and their prompt mode is automatically 'NAME'
    pool = ["H", "W", "X", "A", "B", "C"]
    chosen_silent_targets: set[str] = set()

    for _ in range(60):
        session = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
        target = session.current_round.target_symbol
        if target in {"H", "W", "X"}:
            chosen_silent_targets.add(target)
            assert session.current_round.prompt_mode == "NAME"
        else:
            assert session.current_round.prompt_mode == "PHONETIC"

    assert len(chosen_silent_targets) > 0, "Silent letters (H, W, X) were never selected as targets!"


def test_phonetic_mode_silent_letters_failure_paths() -> None:
    # Failure path 1: Cannot process guess in already finished session
    pool = ["H", "W", "X", "A", "B"]
    session = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
    session.is_game_over = True
    with pytest.raises(RuntimeError, match="CRITICAL: Cannot guess in a finished game session"):
        session.process_guess("H")

    # Failure path 2: Cannot process guess after round already solved
    session2 = GameSession(pool, ask_letter_names=False, ask_letter_sounds=True)
    target = session2.current_round.target_symbol
    assert session2.process_guess(target)
    with pytest.raises(RuntimeError, match="CRITICAL: Current round is already solved"):
        session2.process_guess(target)


def test_case_insensitive_collision_avoidance_and_k_fallback() -> None:
    # 1 Happy Path: Pool with both uppercase and lowercase ('A', 'a', 'B', 'b', 'C', 'D', 'E')
    # never displays both cases of the same letter in the same round or consecutive targets.
    mixed_pool = ["A", "a", "B", "b", "C", "D", "E"]
    for _ in range(15):
        session = GameSession(mixed_pool, ask_letter_names=True, ask_letter_sounds=True)
        prev_upper = session.current_round.target_symbol.upper()
        while True:
            uppers = [s.upper() for s in session.current_round.displayed_symbols]
            assert len(uppers) == len(set(uppers)), f"Duplicate case-insensitive letters on screen: {session.current_round.displayed_symbols}"
            assert session.process_guess(session.current_round.target_symbol)
            if not session.advance_to_next_round():
                break
            curr_upper = session.current_round.target_symbol.upper()
            assert curr_upper != prev_upper
            prev_upper = curr_upper

    # 2 Happy Path: 5-symbol pool with 3 K-sound letters ('C', 'K', 'Q', 'A', 'B')
    # completes all 10 rounds in sound-only mode by falling back to NAME in 4-5 card rounds.
    k_heavy_pool = ["C", "K", "Q", "A", "B"]
    session_k = GameSession(k_heavy_pool, ask_letter_names=False, ask_letter_sounds=True)
    for _ in range(TOTAL_ROUNDS - 1):
        assert session_k.process_guess(session_k.current_round.target_symbol)
        assert session_k.advance_to_next_round()
    assert session_k.process_guess(session_k.current_round.target_symbol)
    assert not session_k.advance_to_next_round()
    assert session_k.is_game_over

    # Failure Path 1: Pool with 5 items but only 3 distinct case-insensitive symbols fails in Round 1
    case_dup_pool = ["A", "a", "B", "b", "A"]
    with pytest.raises(ValueError, match="CRITICAL: Not enough distractors"):
        GameSession(case_dup_pool)

    # Failure Path 2: Pool where all symbols match previous target case-insensitively raises ValueError
    session_err = GameSession(["A", "B", "C", "D", "E"])
    session_err.symbol_pool = ["a", "A"]
    with pytest.raises(ValueError, match="CRITICAL: No available targets after excluding previous target"):
        session_err._init_round(2, previous_target="A")




