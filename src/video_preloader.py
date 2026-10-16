from pathlib import Path
import threading
from typing import TYPE_CHECKING
import pygame

from src.animal_manager import AnimalManager
from src.video_player import AnimalVideoPlayer, find_ffmpeg_executable, probe_video_dimensions


class VideoPreloader:
    def __init__(self, animal_mgr: AnimalManager) -> None:
        if not isinstance(animal_mgr, AnimalManager):
            raise TypeError(f"CRITICAL: animal_mgr must be an AnimalManager, got {type(animal_mgr).__name__}")
        self.animal_mgr: AnimalManager = animal_mgr
        self._lock: threading.Lock = threading.Lock()
        self._cond: threading.Condition = threading.Condition(self._lock)
        self._preloaded_players: dict[int, AnimalVideoPlayer] = {}
        self._poster_surfaces: dict[int, pygame.Surface] = {}
        self._warmup_started: bool = False
        self._preloading_scores: set[int] = set()

    def start_warmup(self, target_height: int) -> None:
        if target_height <= 0:
            raise ValueError(f"CRITICAL: target_height must be positive, got {target_height}")
        with self._cond:
            if self._warmup_started:
                return
            self._warmup_started = True

        thread = threading.Thread(target=self._warmup_worker, args=(target_height,), daemon=True)
        thread.start()

    def _warmup_worker(self, target_height: int) -> None:
        for score in range(11):
            if not self.animal_mgr.has_video(score):
                continue
            vpath = self.animal_mgr.get_video_path(score)
            if vpath is None or not vpath.is_file():
                continue
            try:
                probe_video_dimensions(vpath)
            except Exception:
                continue

    def preload_video(self, score: int, target_height: int) -> None:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
        if target_height <= 0:
            raise ValueError(f"CRITICAL: target_height must be positive, got {target_height}")

        if not self.animal_mgr.has_video(score):
            return

        with self._cond:
            if score in self._preloaded_players or score in self._preloading_scores:
                return
            self._preloading_scores.add(score)

        thread = threading.Thread(target=self._preload_worker, args=(score, target_height), daemon=True)
        thread.start()

    def _preload_worker(self, score: int, target_height: int) -> None:
        vpath = self.animal_mgr.get_video_path(score)
        if vpath is None or not vpath.is_file():
            with self._cond:
                self._preloading_scores.discard(score)
                self._cond.notify_all()
            return

        player: AnimalVideoPlayer | None = None
        try:
            player = AnimalVideoPlayer(video_path=vpath, target_height=target_height)
            with self._cond:
                if score in self._preloading_scores:
                    self._preloaded_players[score] = player
                    player = None
        except Exception:
            pass
        finally:
            if player is not None:
                player.close()
            with self._cond:
                self._preloading_scores.discard(score)
                self._cond.notify_all()

    def get_or_create_player(self, score: int, target_height: int) -> AnimalVideoPlayer | None:
        if not isinstance(score, int):
            raise TypeError(f"CRITICAL: score must be an int, got {type(score).__name__}")
        if score < 0 or score > 10:
            raise ValueError(f"CRITICAL: score must be between 0 and 10, got {score}")
        if target_height <= 0:
            raise ValueError(f"CRITICAL: target_height must be positive, got {target_height}")

        if not self.animal_mgr.has_video(score):
            return None

        with self._cond:
            if score in self._preloading_scores and score not in self._preloaded_players:
                self._cond.wait(timeout=1.5)
            if score in self._preloaded_players:
                return self._preloaded_players.pop(score)

        vpath = self.animal_mgr.get_video_path(score)
        if vpath is None or not vpath.is_file():
            return None

        try:
            return AnimalVideoPlayer(video_path=vpath, target_height=target_height)
        except Exception:
            return None

    def cleanup_unused(self, keep_score: int | None = None) -> None:
        with self._cond:
            self._preloading_scores = {s for s in self._preloading_scores if s == keep_score}
            scores_to_remove = [s for s in self._preloaded_players if s != keep_score]
            for s in scores_to_remove:
                player = self._preloaded_players.pop(s)
                player.close()
            self._cond.notify_all()

    def close_all(self) -> None:
        with self._cond:
            self._preloading_scores.clear()
            for player in self._preloaded_players.values():
                player.close()
            self._preloaded_players.clear()
            self._cond.notify_all()
