import pygame
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from src.menu_screens import MainMenuScreen
from src.font_manager import FontManager

def capture_main_menu():
    pygame.init()
    pygame.font.init()

    w, h = 1920, 1080
    surf = pygame.Surface((w, h))
    fm = FontManager()
    menu = MainMenuScreen(w, h)
    menu.render(surf, fm, (0, 0))

    out_path = "scripts/preview_menu_option_a_live.png"
    pygame.image.save(surf, out_path)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    capture_main_menu()
