from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_all_audio import (
    AudioItem,
    build_audio_manifest,
    copy_sfx_assets,
    get_style_prompt,
)


def test_build_audio_manifest_count_and_structure() -> None:
    manifest = build_audio_manifest()
    # 26 letters * 3 = 78, 20 numbers * 3 = 60 => total 138
    assert len(manifest) == 138

    letters = [item for item in manifest if item.category == "letter"]
    numbers = [item for item in manifest if item.category == "number"]
    assert len(letters) == 78
    assert len(numbers) == 60

    # Verify first and last items
    assert letters[0].filename == "q_letter_A.mp3"
    assert letters[0].text == "Où est la lettre A ?"
    assert numbers[-1].filename == "ans_neg_number_20.mp3"
    assert numbers[-1].text == "Non, c'est le chiffre 20."


def test_get_style_prompt_happy_paths() -> None:
    item_q = AudioItem(
        filename="q_letter_A.mp3",
        text="Où est la lettre A ?",
        category="letter",
        utterance_type="question",
        symbol="A",
    )
    prompt_f = get_style_prompt("FEMALE", item_q)
    prompt_m = get_style_prompt("MALE", item_q)

    assert "d'institutrice" in prompt_f
    assert "d'instituteur" in prompt_m
    assert "français" in prompt_f and "français" in prompt_m


def test_get_style_prompt_unknown_utterance_type() -> None:
    item_invalid = AudioItem(
        filename="test.mp3",
        text="Test",
        category="letter",
        utterance_type="invalid_type",
        symbol="A",
    )
    with pytest.raises(ValueError, match="CRITICAL: Unknown utterance type"):
        get_style_prompt("FEMALE", item_invalid)


def test_copy_sfx_assets(tmp_path: Path) -> None:
    src_dir = tmp_path / "sounds_downloaded"
    src_dir.mkdir()
    (src_dir / "selection_correct.mp3").write_bytes(b"correct-mp3")
    (src_dir / "selection_wrong.wav").write_bytes(b"wrong-wav")

    copy_sfx_assets(tmp_path)

    dst_dir = tmp_path / "assets" / "audio" / "sfx"
    assert (dst_dir / "correct.mp3").is_file()
    assert (dst_dir / "correct.mp3").read_bytes() == b"correct-mp3"
    assert (dst_dir / "wrong.wav").is_file()
    assert (dst_dir / "wrong.wav").read_bytes() == b"wrong-wav"
