from pathlib import Path
import pygame

def test_svg():
    pygame.init()
    svg_path = Path("scripts/sample.svg")
    svg_path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        '<circle cx="50" cy="50" r="40" fill="red"/>'
        '</svg>',
        encoding="utf-8"
    )
    try:
        surf = pygame.image.load(str(svg_path))
        print("pygame.image.load succeeded with size:", surf.get_size())
    except Exception as e:
        print("pygame.image.load failed on SVG:", type(e).__name__, e)
    finally:
        if svg_path.is_file():
            svg_path.unlink()

if __name__ == "__main__":
    test_svg()
