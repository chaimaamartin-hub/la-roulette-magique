import pygame
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from src.ui_elements import UIIconButton

def render_fine_tuned():
    pygame.init()
    pygame.font.init()

    w, h = 1920, 1080
    scale = 1.0
    center_x = w // 2
    center_y = h // 2

    play_sz = int(130 * scale)
    sub_sz = int(80 * scale)

    def base_menu():
        s = pygame.Surface((w, h))
        s.fill((255, 255, 255))
        btn_play = UIIconButton(
            rect=pygame.Rect(center_x - play_sz // 2, center_y - int(45 * scale), play_sz, play_sz),
            icon_type="PLAY",
            bg_color=(20, 20, 25),
            hover_color=(50, 50, 60),
            icon_color=(255, 255, 255),
            border_radius=max(18, int(play_sz * 0.22)),
        )
        btn_config = UIIconButton(
            rect=pygame.Rect(center_x - sub_sz // 2, center_y + int(110 * scale), sub_sz, sub_sz),
            icon_type="GEAR",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(sub_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )
        btn_quit = UIIconButton(
            rect=pygame.Rect(center_x - sub_sz // 2, center_y + int(210 * scale), sub_sz, sub_sz),
            icon_type="EXIT",
            bg_color=(255, 255, 255),
            hover_color=(240, 240, 245),
            icon_color=(20, 20, 25),
            border_radius=max(12, int(sub_sz * 0.22)),
            border_color=(20, 20, 25),
            border_width=3,
        )
        btn_play.render(s, (0, 0))
        btn_config.render(s, (0, 0))
        btn_quit.render(s, (0, 0))
        return s

    def render_smooth(text, font_name, size, color, bold=True):
        f = pygame.font.SysFont(font_name, size * 2, bold=bold)
        raw = f.render(text, True, color)
        return pygame.transform.smoothscale(raw, (raw.get_width() // 2, raw.get_height() // 2))

    # Variant 1: Pure crisp Trebuchet MS (no shadow, 100% clean anti-aliasing)
    s1 = base_menu()
    t1 = render_smooth("LES CARTES MAGIQUES", "Trebuchet MS", 72, (20, 20, 25), bold=True)
    r1 = t1.get_rect(center=(center_x, center_y - int(160 * scale)))
    s1.blit(t1, r1)
    pygame.image.save(s1, "scripts/preview_menu_pure_clean.png")

    # Variant 2: Crisp Segoe UI Bold (no shadow, ultra-clean)
    s2 = base_menu()
    t2 = render_smooth("LES CARTES MAGIQUES", "Segoe UI", 72, (20, 20, 25), bold=True)
    r2 = t2.get_rect(center=(center_x, center_y - int(160 * scale)))
    s2.blit(t2, r2)
    pygame.image.save(s2, "scripts/preview_menu_segoe_clean.png")

    # Variant 3: Magical Dual-Tone (Navy + Golden Magiques) with star
    s3 = base_menu()
    p1 = render_smooth("LES CARTES ", "Trebuchet MS", 70, (28, 32, 44), bold=True)
    p2 = render_smooth("MAGIQUES", "Trebuchet MS", 70, (230, 155, 20), bold=True)
    w_tot = p1.get_width() + p2.get_width()
    h_tot = max(p1.get_height(), p2.get_height())
    c3 = pygame.Surface((w_tot, h_tot), pygame.SRCALPHA)
    c3.blit(p1, (0, 0))
    c3.blit(p2, (p1.get_width(), 0))
    r3 = c3.get_rect(center=(center_x, center_y - int(160 * scale)))
    s3.blit(c3, r3)
    pygame.image.save(s3, "scripts/preview_menu_dualtone.png")

    print("Saved fine-tuned menu previews.")

if __name__ == "__main__":
    render_fine_tuned()
