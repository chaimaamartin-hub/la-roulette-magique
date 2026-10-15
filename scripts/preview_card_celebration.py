from pathlib import Path
import sys
import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.card import Card


def generate_celebration_previews() -> None:
    pygame.init()
    pygame.font.init()

    w, h = 800, 400
    surf = pygame.Surface((w, h))
    font = pygame.font.SysFont(["segoeui", "arial"], 80, bold=True)

    target_r1 = pygame.Rect(120, 80, 180, 240)
    target_r2 = pygame.Rect(340, 80, 180, 240)
    target_r3 = pygame.Rect(560, 80, 180, 240)

    # Card 1: During rainbow flash (t=0.3s)
    c1 = Card("A", 0, target_r1, w)
    c1.state = "RAINBOW_FLASH"
    c1.is_correct = True
    c1.state_time = 0.3
    c1.correct_anim_time = 0.3
    c1.current_x = float(target_r1.x)

    # Card 2: After flash, in IDLE celebrating (t=1.2s)
    c2 = Card("B", 1, target_r2, w)
    c2.state = "IDLE"
    c2.is_correct = True
    c2.state_time = 0.4
    c2.correct_anim_time = 1.2
    c2.current_x = float(target_r2.x)

    # Card 3: Normal unselected card for comparison
    c3 = Card("C", 2, target_r3, w)
    c3.state = "IDLE"
    c3.current_x = float(target_r3.x)

    surf.fill((255, 255, 255))
    c3.render(surf, font)
    c2.render(surf, font)
    c1.render(surf, font)

    out_path = Path(__file__).resolve().parent / "preview_card_celebration.png"
    pygame.image.save(surf, str(out_path))
    print(f"Saved preview: {out_path}")
    pygame.quit()


if __name__ == "__main__":
    generate_celebration_previews()
