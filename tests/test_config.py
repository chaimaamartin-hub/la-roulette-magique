from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import (
    DEFAULT_LETTERS,
    DEFAULT_NUMBERS,
    GameConfig,
    load_config,
    save_config,
)


def test_config_defaults_and_validation() -> None:
    cfg = GameConfig()
    cfg.validate()
    assert set(DEFAULT_LETTERS).issubset(set(cfg.selected_symbols))
    assert set(DEFAULT_NUMBERS).issubset(set(cfg.selected_symbols))
    assert len(cfg.selected_symbols) >= 5


def test_config_validation_too_few_symbols() -> None:
    cfg = GameConfig(selected_symbols=["A", "B", "1"])
    with pytest.raises(ValueError, match="CRITICAL: At least 5 symbols must be selected"):
        cfg.validate()


def test_config_validation_invalid_symbol() -> None:
    cfg = GameConfig(selected_symbols=["A", "B", "C", "D", "INVALID_SYM"])
    with pytest.raises(ValueError, match="CRITICAL: Unknown symbol"):
        cfg.validate()


def test_save_and_load_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    cfg = GameConfig(selected_symbols=["A", "B", "C", "1", "2"])
    saved_path = save_config(cfg, config_file)
    assert saved_path == config_file
    assert config_file.is_file()

    loaded = load_config(config_file)
    assert loaded.selected_symbols == ["A", "B", "C", "1", "2"]


def test_load_config_corrupt_json(tmp_path: Path) -> None:
    config_file = tmp_path / "corrupt.json"
    config_file.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(ValueError, match="CRITICAL: Invalid configuration file"):
        load_config(config_file)


def test_get_default_config_path_frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.config import get_default_config_path
    fake_exe = "C:/games/app.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", fake_exe, raising=False)

    resolved = get_default_config_path()
    assert resolved == Path("C:/games/config.json")


def test_config_prompt_modes_validation() -> None:
    # Happy paths
    cfg_names = GameConfig(ask_letter_names=True, ask_letter_sounds=False)
    cfg_names.validate()
    cfg_sounds = GameConfig(ask_letter_names=False, ask_letter_sounds=True)
    cfg_sounds.validate()
    cfg_both = GameConfig(ask_letter_names=True, ask_letter_sounds=True)
    cfg_both.validate()

    # Failure path 1: Both prompt modes disabled
    cfg_none = GameConfig(ask_letter_names=False, ask_letter_sounds=False)
    with pytest.raises(ValueError, match="CRITICAL: At least one prompt mode"):
        cfg_none.validate()


def test_save_and_load_config_with_prompt_modes(tmp_path: Path) -> None:
    config_file = tmp_path / "config_modes.json"
    cfg = GameConfig(
        selected_symbols=["A", "B", "C", "1", "2"],
        ask_letter_names=False,
        ask_letter_sounds=True,
    )
    save_config(cfg, config_file)
    loaded = load_config(config_file)
    assert not loaded.ask_letter_names
    assert loaded.ask_letter_sounds


