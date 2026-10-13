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


@dataclass
class RoundData:
    round_index: int
    target_symbol: str
    displayed_symbols: list[str]
    voice_type: Literal["FEMALE", "MALE"]
    first_attempt_success: bool = True
    is_solved: bool = False
    attempts: int = 0


class GameSession:
    def __init__(self, symbol_pool: list[str]) -> None:
        if len(symbol_pool) < 5:
            raise ValueError(
                f"CRITICAL: symbol_pool must have at least 5 symbols, got {len(symbol_pool)}."
            )
        self.symbol_pool: list[str] = list(symbol_pool)
        self.current_round_num: int = 1
        self.score: int = 0
        self.current_round: RoundData = self._init_round(1)
        self.is_game_over: bool = False

    def _init_round(self, round_num: int) -> RoundData:
        count = get_symbol_count_for_round(round_num)
        target = random.choice(self.symbol_pool)

        remaining = [s for s in self.symbol_pool if s != target]
        if len(remaining) < count - 1:
            raise ValueError("CRITICAL: Not enough distractors in pool.")

        distractors = random.sample(remaining, count - 1)
        symbols = distractors + [target]
        random.shuffle(symbols)

        voice: Literal["FEMALE", "MALE"] = random.choice(["FEMALE", "MALE"])
        return RoundData(
            round_index=round_num,
            target_symbol=target,
            displayed_symbols=symbols,
            voice_type=voice,
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

        if self.current_round_num >= TOTAL_ROUNDS:
            self.is_game_over = True
            return False

        self.current_round_num += 1
        self.current_round = self._init_round(self.current_round_num)
        return True

    def get_star_rating(self) -> int:
        if self.score >= 8:
            return 3
        if self.score >= 5:
            return 2
        if self.score >= 1:
            return 1
        return 0
