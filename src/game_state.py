from dataclasses import dataclass, field
import random
from typing import Literal

TOTAL_ROUNDS: int = 10


def get_symbol_count_for_round(round_number: int) -> int:
    if not (1 <= round_number <= TOTAL_ROUNDS):
        raise ValueError(f"CRITICAL: round_number must be 1..{TOTAL_ROUNDS}, got {round_number}.")
    if round_number <= 4:
        return 3
    if round_number <= 7:
        return 4
    return 5


PromptMode = Literal["NAME", "PHONETIC"]
SILENT_OR_AMBIGUOUS_LETTERS: set[str] = {"H", "W", "X", "h", "w", "x"}
K_SOUND_LETTERS: set[str] = {"C", "K", "Q", "c", "k", "q"}


@dataclass
class RoundData:
    round_index: int
    target_symbol: str
    displayed_symbols: list[str]
    voice_type: Literal["FEMALE", "MALE"]
    prompt_mode: PromptMode = "NAME"
    first_attempt_success: bool = True
    is_solved: bool = False
    attempts: int = 0


class GameSession:
    def __init__(
        self,
        symbol_pool: list[str],
        ask_letter_names: bool = True,
        ask_letter_sounds: bool = False,
    ) -> None:
        if not ask_letter_names and not ask_letter_sounds:
            raise ValueError(
                "CRITICAL: At least one prompt mode (names or sounds) must be enabled."
            )
        if len(symbol_pool) < 5:
            raise ValueError(
                f"CRITICAL: symbol_pool must have at least 5 symbols, got {len(symbol_pool)}."
            )
        self.symbol_pool: list[str] = list(symbol_pool)
        self.ask_letter_names: bool = ask_letter_names
        self.ask_letter_sounds: bool = ask_letter_sounds
        self.current_round_num: int = 1
        self.score: int = 0
        self.round_results: list[bool] = []
        self.current_round: RoundData = self._init_round(1, None)
        self.is_game_over: bool = False

    def _init_round(self, round_num: int, previous_target: str | None) -> RoundData:
        if not (1 <= round_num <= TOTAL_ROUNDS):
            raise ValueError(f"CRITICAL: round_num must be 1..{TOTAL_ROUNDS}, got {round_num}.")
        count = get_symbol_count_for_round(round_num)

        available_targets = [s for s in self.symbol_pool if s != previous_target]
        if not available_targets:
            raise ValueError("CRITICAL: No available targets after excluding previous target.")

        # Determine target and prompt mode
        if self.ask_letter_sounds and not self.ask_letter_names:
            # All available targets are eligible; numbers and silent/ambiguous letters (H, W, X)
            # seamlessly fall back to letter/number name prompt instead of being skipped.
            target = random.choice(available_targets)
            if target.isdigit() or target in SILENT_OR_AMBIGUOUS_LETTERS:
                prompt_mode: PromptMode = "NAME"
            else:
                prompt_mode = "PHONETIC"
        elif self.ask_letter_sounds and self.ask_letter_names:
            # Both modes active: randomly choose between name and phonetic for eligible letters
            target = random.choice(available_targets)
            if not target.isdigit() and target not in SILENT_OR_AMBIGUOUS_LETTERS:
                prompt_mode = random.choice(["NAME", "PHONETIC"])
            else:
                prompt_mode = "NAME"
        else:
            # Letter names only
            target = random.choice(available_targets)
            prompt_mode = "NAME"

        remaining = [s for s in self.symbol_pool if s != target]

        # Enforce phonetic collision rules: C, K, Q can never appear together
        if prompt_mode == "PHONETIC" and target in K_SOUND_LETTERS:
            remaining = [s for s in remaining if s not in K_SOUND_LETTERS]

        if len(remaining) < count - 1:
            raise ValueError("CRITICAL: Not enough distractors in pool satisfying phonetic constraints.")

        distractors = random.sample(remaining, count - 1)
        symbols = distractors + [target]
        random.shuffle(symbols)

        voice: Literal["FEMALE", "MALE"] = random.choice(["FEMALE", "MALE"])
        return RoundData(
            round_index=round_num,
            target_symbol=target,
            displayed_symbols=symbols,
            voice_type=voice,
            prompt_mode=prompt_mode,
        )

    def process_guess(self, symbol: str) -> bool:
        if self.is_game_over:
            raise RuntimeError("CRITICAL: Cannot guess in a finished game session.")
        if self.current_round.is_solved:
            raise RuntimeError("CRITICAL: Current round is already solved.")

        is_correct = symbol == self.current_round.target_symbol
        if is_correct:
            self.current_round.is_solved = True
            if self.current_round.attempts == 0 and self.current_round.first_attempt_success:
                self.score += 1
            return True

        self.current_round.attempts += 1
        self.current_round.first_attempt_success = False
        return False

    def advance_to_next_round(self) -> bool:
        if not self.current_round.is_solved:
            raise RuntimeError("CRITICAL: Cannot advance round before target is solved.")

        self.round_results.append(self.current_round.first_attempt_success)

        if self.current_round_num >= TOTAL_ROUNDS:
            self.is_game_over = True
            return False

        self.current_round_num += 1
        self.current_round = self._init_round(
            self.current_round_num, self.current_round.target_symbol
        )
        return True

    def get_star_rating(self) -> int:
        if self.score >= 8:
            return 3
        if self.score >= 5:
            return 2
        if self.score >= 1:
            return 1
        return 0
