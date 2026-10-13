from pathlib import Path
import sys
import pygame
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ui_elements import UIButton, UICheckbox


def test_ui_button_clicks_and_hover() -> None:
    btn = UIButton(rect=pygame.Rect(100, 100, 200, 60), text="Jouer")
    assert btn.is_hovered((150, 120))
    assert not btn.is_hovered((50, 50))

    assert btn.is_clicked((150, 120))
    assert not btn.is_clicked((350, 120))


def test_ui_checkbox_toggle_and_click() -> None:
    box = UICheckbox(rect=pygame.Rect(50, 50, 40, 40), label="A", checked=False)
    assert not box.checked

    assert box.is_clicked((60, 60))
    assert not box.is_clicked((10, 10))

    assert box.toggle()  # now True
    assert box.checked
    assert not box.toggle()  # now False
    assert not box.checked
