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


def test_get_app_icon_path() -> None:
    from main import get_app_icon_path

    # Happy path: Returns path to app_icon.png and the file exists
    icon_path = get_app_icon_path()
    assert isinstance(icon_path, Path)
    assert icon_path.is_file()
    assert icon_path.name == "app_icon.png"


def test_parse_args_failure_paths() -> None:
    # Failure path 1: Invalid integer width
    with pytest.raises(SystemExit):
        parse_args(["--width", "not_a_number"])

    # Failure path 2: Unrecognized CLI argument
    with pytest.raises(SystemExit):
        parse_args(["--unknown-flag"])

