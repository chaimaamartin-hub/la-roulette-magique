from pathlib import Path
import sys
import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.star_renderer import draw_progress_stars


def generate_star_previews() -> None:
    pygame.init()
    w, h = 900, 300
    surf = pygame.Surface((w, h))

    # Test round results: 7 correct, 1 wrong, 2 unplayed
    results = [True, True, True, True, False, True, True, True]

    timestamps = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, t in enumerate(timestamps):
        surf.fill((255, 255, 255))
        draw_progress_stars(
            surface=surf,
            center_pos=(w // 2, h // 2),
            round_results=results,
            total_rounds=10,
            radius=24,
            spacing=64,
            anim_time=t,
        )
        out_path = out_dir / f"preview_stars_t{i}.png"
        pygame.image.save(surf, str(out_path))
        print(f"Saved preview: {out_path}")

    # Also save high-resolution closeup
    closeup_surf = pygame.Surface((400, 150))
    closeup_surf.fill((255, 255, 255))
    draw_progress_stars(
        surface=closeup_surf,
        center_pos=(200, 75),
        round_results=[True, False],
        total_rounds=3,
        radius=28,
        spacing=100,
        anim_time=0.4,
    )
    closeup_path = out_dir / "preview_star_closeup.png"
    pygame.image.save(closeup_surf, str(closeup_path))
    print(f"Saved closeup: {closeup_path}")

    pygame.quit()


if __name__ == "__main__":
    generate_star_previews()
