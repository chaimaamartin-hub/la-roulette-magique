from pathlib import Path
import shutil
import subprocess
import sys
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

    # 4. imageio_ffmpeg binary if present
    try:
        import imageio_ffmpeg

        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_bin and Path(ffmpeg_bin).is_file():
            return Path(ffmpeg_bin)
    except ImportError:
        pass

    raise FileNotFoundError("CRITICAL: ffmpeg executable is required for video playback but was not found.")


def probe_video_dimensions(ffmpeg_bin: Path, video_path: Path) -> tuple[int, int]:
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    res = subprocess.run(
        [str(ffmpeg_bin), "-i", str(video_path)],
        capture_output=True,
        text=True,
        creationflags=creationflags,
    )
    import re

    m = re.search(r"Stream.*Video:.*,\s*(\d+)x(\d+)", res.stderr)
    if not m:
        raise RuntimeError(f"CRITICAL: Failed to probe video dimensions from {video_path}")
    return int(m.group(1)), int(m.group(2))


class AnimalVideoPlayer:
    def __init__(
        self,
        video_path: Path,
        target_height: int,
        target_width: int | None = None,
        fps: int = 24,
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
        self.ffmpeg_bin: Path = find_ffmpeg_executable()

        if target_width is not None:
            self.width: int = (target_width // 2) * 2
            self.height: int = (target_height // 2) * 2
        else:
            orig_w, orig_h = probe_video_dimensions(self.ffmpeg_bin, self.video_path)
            self.height = (target_height // 2) * 2
            calc_w = int(round(self.height * (orig_w / float(orig_h))))
            self.width = (calc_w // 2) * 2

        self.frame_bytes: int = self.width * self.height * 3
        self.elapsed: float = 0.0
        self.is_finished: bool = False

        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        cmd = [
            str(self.ffmpeg_bin),
            "-i",
            str(self.video_path),
            "-an",  # Audio disabled: volume strictly 0
            "-vf",
            f"fps={self.fps},scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:color=white,colorlevels=rimax=245/255:gimax=245/255:bimax=245/255",
            "-f",
            "image2pipe",
            "-pix_fmt",
            "rgb24",
            "-vcodec",
            "rawvideo",
            "-",
        ]

        self.process: subprocess.Popen[bytes] | None = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )

        if self.process.stdout is None:
            self.close()
            raise RuntimeError("CRITICAL: Video process stdout is None")

        raw_frame = self.process.stdout.read(self.frame_bytes)
        if len(raw_frame) != self.frame_bytes:
            self.close()
            raise RuntimeError(f"CRITICAL: Failed to decode initial video frame from {self.video_path}")

        self.current_surface: pygame.Surface = pygame.image.frombuffer(
            raw_frame, (self.width, self.height), "RGB"
        )

    def update(self, dt: float) -> None:
        if self.process is None or self.process.stdout is None or self.is_finished:
            return

        self.elapsed += dt
        while self.elapsed >= self.frame_interval:
            self.elapsed -= self.frame_interval
            raw_frame = self.process.stdout.read(self.frame_bytes)
            if len(raw_frame) == self.frame_bytes:
                self.current_surface = pygame.image.frombuffer(
                    raw_frame, (self.width, self.height), "RGB"
                )
            else:
                self.is_finished = True
                break

    def get_current_frame(self) -> pygame.Surface:
        return self.current_surface

    def close(self) -> None:
        if getattr(self, "process", None) is not None:
            try:
                self.process.kill()
            except Exception:
                pass
            self.process = None

    def __del__(self) -> None:
        self.close()
