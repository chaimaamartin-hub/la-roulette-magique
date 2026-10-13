from pathlib import Path
import pygame

def test():
    pygame.init()
    svg_path = Path("scripts/gear_v2.svg")
    loaded = pygame.image.load(str(svg_path))
    size = 48
    scaled = pygame.transform.smoothscale(loaded, (size, size))
    
    # Tint with red or light gray or white
    for color in [(255, 255, 255), (200, 200, 200), (235, 165, 0)]:
        tinted = scaled.copy()
        if color != (255, 255, 255):
            tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        print("Tinted", color, "pixels:", tinted.get_at((size//2, 10)))

if __name__ == "__main__":
    test()
