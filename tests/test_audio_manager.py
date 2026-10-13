from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.audio_manager import AudioManager


@pytest.fixture(scope="module", autouse=True)
def init_pygame_mixer() -> None:
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def test_resolve_audio_path_letter_and_number() -> None:
    am = AudioManager()
    am.set_voice("FEMALE")
    # Uppercase letter
    p1 = am.resolve_audio_path("A", "question")
    assert p1.name == "q_letter_A.mp3"
    assert "voice_female" in str(p1)

    # Lowercase letter normalized to uppercase file
    p2 = am.resolve_audio_path("b", "ans_pos")
    assert p2.name == "ans_pos_letter_B.mp3"

    # Number
    p3 = am.resolve_audio_path("7", "ans_neg")
    assert p3.name == "ans_neg_number_7.mp3"

    # Switch voice to male
    am.set_voice("MALE")
    p4 = am.resolve_audio_path("A", "question")
    assert "voice_male" in str(p4)


def test_resolve_audio_path_empty_symbol() -> None:
    am = AudioManager()
    with pytest.raises(ValueError, match="CRITICAL: Symbol cannot be empty"):
        am.resolve_audio_path("   ", "question")


def test_resolve_audio_path_invalid_voice() -> None:
    am = AudioManager()
    with pytest.raises(ValueError, match="CRITICAL: Unknown voice"):
        am.set_voice("INVALID"  # type: ignore[arg-type]
        )


def test_play_voice_missing_file(tmp_path: Path) -> None:
    am = AudioManager(assets_dir=tmp_path / "assets")
    with pytest.raises(FileNotFoundError, match="CRITICAL: Voice file not found"):
        am.play_voice("A", "question")


def test_get_default_assets_dir_frozen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.audio_manager import get_default_assets_dir

    assets_folder = tmp_path / "assets" / "audio"
    assets_folder.mkdir(parents=True)

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    resolved = get_default_assets_dir()
    assert resolved == assets_folder

