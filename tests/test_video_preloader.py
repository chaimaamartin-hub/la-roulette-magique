from pathlib import Path
import sys
import time
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.animal_manager import AnimalManager
from src.video_player import AnimalVideoPlayer
from src.video_preloader import VideoPreloader


def test_video_preloader_happy_path() -> None:
    animal_mgr = AnimalManager()
    preloader = VideoPreloader(animal_mgr)

    # Happy path: start warmup and preload score 10 (bear)
    preloader.start_warmup(240)
    preloader.preload_video(10, 240)

    # Allow worker thread a brief moment to instantiate
    time.sleep(0.3)

    player = preloader.get_or_create_player(10, 240)
    assert player is not None
    assert isinstance(player, AnimalVideoPlayer)

    frame = player.get_current_frame()
    assert isinstance(frame, pygame.Surface)
    assert frame.get_height() == 240

    # Cleanup unused and close all
    preloader.cleanup_unused(keep_score=10)
    player.close()
    preloader.close_all()


def test_video_preloader_invalid_inputs_failure_path() -> None:
    with pytest.raises(TypeError, match="CRITICAL: animal_mgr must be an AnimalManager"):
        VideoPreloader("invalid_manager")  # type: ignore[arg-type]

    animal_mgr = AnimalManager()
    preloader = VideoPreloader(animal_mgr)

    # Score out of bounds (< 0 or > 10)
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        preloader.preload_video(-1, 300)
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        preloader.preload_video(11, 300)

    # Score wrong type
    with pytest.raises(TypeError, match="CRITICAL: score must be an int"):
        preloader.preload_video("10", 300)  # type: ignore[arg-type]

    # get_or_create_player validations
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        preloader.get_or_create_player(-1, 300)
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        preloader.get_or_create_player(12, 300)
    with pytest.raises(TypeError, match="CRITICAL: score must be an int"):
        preloader.get_or_create_player(None, 300)  # type: ignore[arg-type]

    preloader.close_all()


def test_video_preloader_invalid_target_height_failure_path() -> None:
    animal_mgr = AnimalManager()
    preloader = VideoPreloader(animal_mgr)

    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.start_warmup(0)
    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.start_warmup(-10)

    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.preload_video(10, 0)
    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.preload_video(10, -50)

    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.get_or_create_player(10, 0)
    with pytest.raises(ValueError, match="CRITICAL: target_height must be positive"):
        preloader.get_or_create_player(10, -20)

    preloader.close_all()


def test_video_preloader_no_video_score(tmp_path: Path) -> None:
    animal_mgr = AnimalManager(videos_dir=tmp_path)
    preloader = VideoPreloader(animal_mgr)

    # Empty directory has no video for any score
    assert animal_mgr.has_video(0) is False
    res = preloader.get_or_create_player(0, 300)
    assert res is None

    preloader.close_all()

