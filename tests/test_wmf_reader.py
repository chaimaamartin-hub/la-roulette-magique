from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.wmf_reader import WMFVideoReader


def test_wmf_video_reader_happy_path() -> None:
    if sys.platform != "win32":
        pytest.skip("WMFVideoReader is supported on Windows")

    video_path = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "score_9_lion.mp4"
    if not video_path.is_file():
        pytest.skip("score_9_lion.mp4 not found")

    reader = WMFVideoReader(video_path)
    width, height = reader.get_dimensions()
    assert width == 1280
    assert height == 720

    frame1 = reader.read_frame_surface()
    assert frame1 is not None
    assert isinstance(frame1, pygame.Surface)
    assert frame1.get_size() == (1280, 720)

    frame2 = reader.read_frame_surface()
    assert frame2 is not None
    assert isinstance(frame2, pygame.Surface)
    assert frame2.get_size() == (1280, 720)

    reader.close()
    assert reader._reader is None


def test_wmf_video_reader_missing_file_failure_path() -> None:
    if sys.platform != "win32":
        pytest.skip("WMFVideoReader is supported on Windows")

    missing = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "non_existent.mp4"
    with pytest.raises(FileNotFoundError, match="CRITICAL: Video file not found"):
        WMFVideoReader(missing)


def test_wmf_video_reader_invalid_type_failure_path() -> None:
    if sys.platform != "win32":
        pytest.skip("WMFVideoReader is supported on Windows")

    with pytest.raises(TypeError, match="CRITICAL: video_path must be a Path"):
        WMFVideoReader("not_a_path")  # type: ignore[arg-type]
