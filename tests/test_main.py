from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import parse_args, SCREEN_WIDTH, SCREEN_HEIGHT


def test_parse_args_defaults() -> None:
    args = parse_args([])
    assert not args.windowed
    assert args.width == SCREEN_WIDTH
    assert args.height == SCREEN_HEIGHT


def test_parse_args_custom() -> None:
    args = parse_args(["--windowed", "--width", "1280", "--height", "720"])
    assert args.windowed
    assert args.width == 1280
    assert args.height == 720
