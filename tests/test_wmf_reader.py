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


def test_wmf_multithreaded_com_init() -> None:
    if sys.platform != "win32":
        pytest.skip("WMFVideoReader is supported on Windows")

    import threading
    from src.wmf_reader import init_media_foundation, _THREAD_LOCAL

    results: list[bool] = []

    def worker() -> None:
        init_media_foundation()
        results.append(bool(getattr(_THREAD_LOCAL, "com_initialized", False)))

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results == [True, True, True]


def test_wmf_video_reader_eof_detection_happy_and_failure_paths() -> None:
    if sys.platform != "win32":
        pytest.skip("WMFVideoReader is supported on Windows")

    video_path = Path(__file__).resolve().parent.parent / "assets" / "videos" / "animals" / "score_9_lion.mp4"
    if not video_path.is_file():
        pytest.skip("score_9_lion.mp4 not found")

    reader = WMFVideoReader(video_path)
    try:
        # 1. Happy path: Read through EOF cleanly without access violation or crash
        frame_count = 0
        while True:
            surf = reader.read_frame_surface()
            if surf is None:
                break
            frame_count += 1

        assert frame_count == 240
        assert reader._is_eof is True

        # 2. Failure path 1: Reading again once _is_eof is True returns None immediately
        assert reader.read_frame_surface() is None
    finally:
        reader.close()

    # 3. Failure path 2: Reading from closed reader returns None
    assert reader.read_frame_surface() is None


