from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.animal_manager import AnimalManager
from src.video_player import AnimalVideoPlayer, find_ffmpeg_executable


def test_find_ffmpeg_executable() -> None:
    exe_path = find_ffmpeg_executable()
    assert isinstance(exe_path, Path)
    assert exe_path.is_file()


def test_animal_video_player_happy_path() -> None:
    # 1 Happy Path: Scale video by target_height while preserving 16:9 aspect ratio
    video_path = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "score_9_lion.mp4"
    if not video_path.is_file():
        pytest.skip("Video file score_9_lion.mp4 not found in assets/videos/animals")

    # Height = 240 -> width proportionally scaled to 426 (16:9)
    player = AnimalVideoPlayer(video_path=video_path, target_height=240, fps=24)
    frame = player.get_current_frame()

    assert isinstance(frame, pygame.Surface)
    assert frame.get_height() == 240
    assert frame.get_width() == 426

    # Margins and corners must be pure solid white (#FFFFFF)
    corner = frame.get_at((0, 0))
    assert (corner.r, corner.g, corner.b) == (255, 255, 255)
    corner_tr = frame.get_at((frame.get_width() - 1, 0))
    assert (corner_tr.r, corner_tr.g, corner_tr.b) == (255, 255, 255)

    # Advance time to trigger next frame decode
    player.update(0.06)
    new_frame = player.get_current_frame()
    assert isinstance(new_frame, pygame.Surface)
    assert new_frame.get_height() == 240

    player.close()
    assert player.process is None


def test_animal_video_player_missing_file_failure_path() -> None:
    # 2 Failure Path A: Missing video file raises FileNotFoundError
    missing = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "non_existent.mp4"
    with pytest.raises(FileNotFoundError, match="CRITICAL"):
        AnimalVideoPlayer(video_path=missing, target_height=200)


def test_animal_video_player_invalid_dimensions_failure_path() -> None:
    # 2 Failure Path B: Non-positive dimensions raise ValueError
    video_path = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "score_9_lion.mp4"
    if not video_path.is_file():
        pytest.skip("Video file score_9_lion.mp4 not found in assets/videos/animals")

    with pytest.raises(ValueError, match="target_height must be positive"):
        AnimalVideoPlayer(video_path=video_path, target_height=0)

    with pytest.raises(ValueError, match="target_height must be positive"):
        AnimalVideoPlayer(video_path=video_path, target_height=-50)

    with pytest.raises(ValueError, match="target_width must be positive"):
        AnimalVideoPlayer(video_path=video_path, target_height=200, target_width=-10)


def test_animal_manager_video_detection() -> None:
    mgr = AnimalManager()
    # Lion (score 9) has video
    assert mgr.has_video(9) is True
    video_path = mgr.get_video_path(9)
    assert video_path is not None
    assert video_path.name == "score_9_lion.mp4"

    # Ant (score 0) has no video yet
    assert mgr.has_video(0) is False
    assert mgr.get_video_path(0) is None

    # Strict Fail fast validation
    with pytest.raises(ValueError):
        mgr.get_video_path(-1)
    with pytest.raises(ValueError):
        mgr.get_video_path(11)
    with pytest.raises(TypeError):
        mgr.get_video_path("9")  # type: ignore[arg-type]


def test_score_screen_video_centering() -> None:
    from src.font_manager import FontManager
    from src.score_screen import ScoreScreen

    screen = ScoreScreen(screen_w=1280, screen_h=720, score=9)
    assert screen.video_player is not None

    frame = screen.video_player.get_current_frame()
    expected_draw_x = screen.animal_pos[0] - frame.get_width() // 2
    # Verify horizontal symmetry around screen center (1280 // 2 = 640)
    center_of_rendered_video = expected_draw_x + frame.get_width() / 2.0
    assert abs(center_of_rendered_video - 640.0) < 1.0

    # Ensure rendering succeeds without errors
    surf = pygame.Surface((1280, 720))
    fm = FontManager()
    screen.render(surf, fm, mouse_pos=(0, 0))
    screen.close()

