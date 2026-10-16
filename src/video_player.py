from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import pygame


def find_ffmpeg_executable() -> Path:
    # 1. Bundled in PyInstaller MEIPASS
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        meipass_ffmpeg = Path(sys._MEIPASS) / "ffmpeg.exe"  # type: ignore[attr-defined]
        if meipass_ffmpeg.is_file():
            return meipass_ffmpeg

    # 2. Next to executable
    exe_dir = Path(sys.executable).parent
    exe_ffmpeg = exe_dir / "ffmpeg.exe"
    if exe_ffmpeg.is_file():
        return exe_ffmpeg

    # 3. System PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return Path(which_ffmpeg)

    raise FileNotFoundError("CRITICAL: ffmpeg executable is required for video playback but was not found.")


from src.wmf_reader import WMFVideoReader, _COLOR_LEVEL_TABLE, init_media_foundation

_DIMENSIONS_CACHE: dict[Path, tuple[int, int]] = {}


def probe_video_dimensions(video_path: Path, ffmpeg_bin: Path | None = None) -> tuple[int, int]:
    if not isinstance(video_path, Path):
        raise TypeError(f"CRITICAL: video_path must be a Path, got {type(video_path).__name__}")
    if not video_path.is_file():
        raise FileNotFoundError(f"CRITICAL: Video file not found at {video_path}")
    if video_path in _DIMENSIONS_CACHE:
        return _DIMENSIONS_CACHE[video_path]

    if sys.platform == "win32":
        reader = WMFVideoReader(video_path)
        dims = reader.get_dimensions()
        reader.close()
        _DIMENSIONS_CACHE[video_path] = dims
        return dims

    bin_path = ffmpeg_bin if ffmpeg_bin is not None else find_ffmpeg_executable()
    res = subprocess.run(
        [str(bin_path), "-i", str(video_path)],
        capture_output=True,
        text=True,
    )
    import re

    m = re.search(r"Stream.*Video:.*,\s*(\d+)x(\d+)", res.stderr)
    if not m:
        raise RuntimeError(f"CRITICAL: Failed to probe video dimensions from {video_path}")
    dims = (int(m.group(1)), int(m.group(2)))
    _DIMENSIONS_CACHE[video_path] = dims
    return dims


class AnimalVideoPlayer:
    def __init__(
        self,
        video_path: Path,
        target_height: int,
        target_width: int | None = None,
        fps: int = 24,
        initial_surface: pygame.Surface | None = None,
    ) -> None:
        if not isinstance(video_path, Path):
            raise TypeError(f"CRITICAL: video_path must be a Path, got {type(video_path).__name__}")
        if not video_path.is_file():
            raise FileNotFoundError(f"CRITICAL: Video file not found at {video_path}")
        if target_height <= 0:
            raise ValueError(f"CRITICAL: target_height must be positive, got {target_height}")
        if target_width is not None and target_width <= 0:
            raise ValueError(f"CRITICAL: target_width must be positive, got {target_width}")
        if fps <= 0:
            raise ValueError(f"CRITICAL: FPS must be positive, got {fps}")

        self.video_path: Path = video_path
        self.fps: int = fps
        self.frame_interval: float = 1.0 / float(fps)
        self.elapsed: float = 0.0
        self.is_finished: bool = False
        self._stop_event: threading.Event = threading.Event()
        self._eof: bool = False
        self._frame_queue: queue.Queue[pygame.Surface] = queue.Queue(maxsize=30)

        if target_width is not None:
            self.width: int = (target_width // 2) * 2
            self.height: int = (target_height // 2) * 2
        else:
            orig_w, orig_h = probe_video_dimensions(self.video_path)
            self.height = (target_height // 2) * 2
            calc_w = int(round(self.height * (orig_w / float(orig_h))))
            self.width = (calc_w // 2) * 2

        self.wmf_reader: WMFVideoReader | None = None
        self.process: subprocess.Popen[bytes] | None = None
        if sys.platform == "win32":
            self.wmf_reader = WMFVideoReader(self.video_path)
            first_frame: pygame.Surface | None = initial_surface
            if first_frame is None:
                decoded = self.wmf_reader.read_frame_surface()
                if decoded is None:
                    self.close()
                    raise RuntimeError(f"CRITICAL: Failed to decode initial video frame from {self.video_path}")
                first_frame = pygame.transform.smoothscale(decoded, (self.width, self.height))
                # Intentional second pass of _COLOR_LEVEL_TABLE after smoothscale: clamps near-white
                # edge/interpolation pixels to pure (255, 255, 255) so no border is visible against the white UI.
                first_frame.get_buffer().write(bytes(first_frame.get_buffer()).translate(_COLOR_LEVEL_TABLE))
            self.current_surface: pygame.Surface = first_frame
            self._reader_thread: threading.Thread = threading.Thread(target=self._wmf_worker, daemon=True)
            self._reader_thread.start()
        else:
            self.ffmpeg_bin: Path = find_ffmpeg_executable()
            self._init_ffmpeg_fallback(initial_surface)

    def _wmf_worker(self) -> None:
        init_media_foundation()
        try:
            while not self._stop_event.is_set():
                if self.wmf_reader is None:
                    break
                raw_surf = self.wmf_reader.read_frame_surface()
                if raw_surf is None:
                    # Intentional: video plays once and stops on the final frame (never loops).
                    self._eof = True
                    break
                scaled = pygame.transform.smoothscale(raw_surf, (self.width, self.height))
                # Intentional second pass after scaling to keep background seamless with pure white canvas.
                scaled.get_buffer().write(bytes(scaled.get_buffer()).translate(_COLOR_LEVEL_TABLE))
                while not self._stop_event.is_set():
                    try:
                        self._frame_queue.put(scaled, timeout=0.05)
                        break
                    except queue.Full:
                        continue
        except Exception:
            self._eof = True


    def _init_ffmpeg_fallback(self, initial_surface: pygame.Surface | None) -> None:
        self.frame_bytes: int = self.width * self.height * 3
        cmd = [
            str(self.ffmpeg_bin),
            "-i",
            str(self.video_path),
            "-an",
            "-vf",
            f"fps={self.fps},scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:color=white",
            "-f",
            "image2pipe",
            "-pix_fmt",
            "rgb24",
            "-vcodec",
            "rawvideo",
            "-",
        ]
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if self.process.stdout is None:
            self.close()
            raise RuntimeError("CRITICAL: Video process stdout is None")
        if initial_surface is not None:
            self.current_surface = initial_surface
        else:
            raw = self.process.stdout.read(self.frame_bytes)
            if len(raw) != self.frame_bytes:
                self.close()
                raise RuntimeError(f"CRITICAL: Failed to decode initial frame from {self.video_path}")
            self.current_surface = pygame.image.frombuffer(raw, (self.width, self.height), "RGB").copy()
        self._reader_thread = threading.Thread(target=self._ffmpeg_worker, daemon=True)
        self._reader_thread.start()

    def _ffmpeg_worker(self) -> None:
        while not self._stop_event.is_set():
            if self.process is None or self.process.stdout is None:
                break
            raw = self.process.stdout.read(self.frame_bytes)
            if len(raw) != self.frame_bytes:
                self._eof = True
                break
            surf = pygame.image.frombuffer(raw, (self.width, self.height), "RGB").copy()
            while not self._stop_event.is_set():
                try:
                    self._frame_queue.put(surf, timeout=0.05)
                    break
                except queue.Full:
                    continue

    def update(self, dt: float) -> None:
        if self.is_finished:
            return

        self.elapsed += dt
        while self.elapsed >= self.frame_interval:
            self.elapsed -= self.frame_interval
            try:
                self.current_surface = self._frame_queue.get_nowait()
            except queue.Empty:
                if self._eof:
                    self.is_finished = True
                break

    def get_current_frame(self) -> pygame.Surface:
        return self.current_surface

    def restart(self) -> None:
        self.close()
        if hasattr(self, "_reader_thread") and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=0.5)

        self._stop_event = threading.Event()
        self._eof = False
        self.is_finished = False
        self.elapsed = 0.0

        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                break

        if sys.platform == "win32":
            self.wmf_reader = WMFVideoReader(self.video_path)
            decoded = self.wmf_reader.read_frame_surface()
            if decoded is not None:
                first_frame = pygame.transform.smoothscale(decoded, (self.width, self.height))
                first_frame.get_buffer().write(bytes(first_frame.get_buffer()).translate(_COLOR_LEVEL_TABLE))
                self.current_surface = first_frame
            self._reader_thread = threading.Thread(target=self._wmf_worker, daemon=True)
            self._reader_thread.start()
        else:
            self._init_ffmpeg_fallback(initial_surface=None)

    def close(self) -> None:
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if getattr(self, "wmf_reader", None) is not None:
            self.wmf_reader.close()
            self.wmf_reader = None
        if getattr(self, "process", None) is not None:
            try:
                self.process.kill()
            except Exception:
                pass
            self.process = None

    def __del__(self) -> None:
        self.close()


