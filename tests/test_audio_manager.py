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


def test_play_animal_sound_happy_path() -> None:
    am = AudioManager()
    # Test all 11 scores (0 through 10) can be loaded and played
    for score in range(11):
        assert am.play_animal_sound(score) is True


def test_play_animal_sound_failure_paths(tmp_path: Path) -> None:
    am = AudioManager()

    # Failure Path 1: Negative score
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        am.play_animal_sound(-1)

    # Failure Path 2: Score > 10
    with pytest.raises(ValueError, match="CRITICAL: score must be between 0 and 10"):
        am.play_animal_sound(11)

    # Failure Path 3: Wrong type
    with pytest.raises(TypeError, match="CRITICAL: score must be an int"):
        am.play_animal_sound("5")  # type: ignore[arg-type]

    # Failure Path 4: Missing animal audio file
    empty_am = AudioManager(assets_dir=tmp_path / "empty_assets")
    with pytest.raises(FileNotFoundError, match="CRITICAL: Animal sound file not found"):
        empty_am.play_animal_sound(0)


def test_resolve_audio_path_phonetic() -> None:
    am = AudioManager()
    am.set_voice("FEMALE")
    p1 = am.resolve_audio_path("A", "question", prompt_mode="PHONETIC")
    assert p1.name == "q_phonetic_A.mp3"

    p2 = am.resolve_audio_path("b", "ans_pos", prompt_mode="PHONETIC")
    assert p2.name == "ans_pos_phonetic_B.mp3"

    # Number should still resolve to number category even if PHONETIC passed
    p3 = am.resolve_audio_path("5", "question", prompt_mode="PHONETIC")
    assert p3.name == "q_number_5.mp3"

    # Failure path: Unknown utterance type
    with pytest.raises(ValueError, match="CRITICAL: Unknown utterance type"):
        am.resolve_audio_path("A", "invalid_type"  # type: ignore[arg-type]
        )



