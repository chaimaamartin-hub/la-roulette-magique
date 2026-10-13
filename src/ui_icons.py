import math
import pygame


def draw_play_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    h = size
    w = int(size * 0.9)
    points = [
        (cx - w // 2, cy - h // 2),
        (cx + w // 2, cy),
        (cx - w // 2, cy + h // 2),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_gear_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    r_outer = radius
    r_inner = int(radius * 0.72)
    cogs = 8
    points: list[tuple[float, float]] = []
    total_steps = cogs * 2

    for i in range(total_steps):
        r = r_outer if i % 2 == 0 else r_inner
        ang = i * (2 * math.pi / total_steps)
        points.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    pygame.draw.polygon(surface, color, points)
    # Inner hole
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), max(3, int(radius * 0.32)))


def draw_close_circle_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    pygame.draw.circle(surface, color, (cx, cy), radius, width=3)
    d = int(radius * 0.45)
    pygame.draw.line(surface, color, (cx - d, cy - d), (cx + d, cy + d), width=3)
    pygame.draw.line(surface, color, (cx - d, cy + d), (cx + d, cy - d), width=3)


def draw_arrow_left_icon(
    surface: pygame.Surface,
    center: tuple[int, int],
    size: int,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    half = size // 2
    # Shaft
    pygame.draw.line(surface, color, (cx - half, cy), (cx + half, cy), width=4)
    # Head
    pygame.draw.line(surface, color, (cx - half, cy), (cx - half // 3, cy - half * 2 // 3), width=4)
    pygame.draw.line(surface, color, (cx - half, cy), (cx - half // 3, cy + half * 2 // 3), width=4)


def draw_progress_circles(
    surface: pygame.Surface,
    center_pos: tuple[int, int],
    round_results: list[bool],
    total_rounds: int = 10,
    radius: int = 16,
    spacing: int = 44,
) -> None:
    cx, cy = center_pos
    total_w = (total_rounds - 1) * spacing
    start_x = cx - total_w // 2

    for i in range(total_rounds):
        x = start_x + i * spacing
        if i < len(round_results):
            if round_results[i]:
                # Full black circle for correct
                pygame.draw.circle(surface, (20, 20, 25), (x, cy), radius)
            else:
                # Empty black circle for wrong
                pygame.draw.circle(surface, (255, 255, 255), (x, cy), radius)
                pygame.draw.circle(surface, (20, 20, 25), (x, cy), radius, width=3)
        else:
            # Greyed out empty circle for unplayed
            pygame.draw.circle(surface, (255, 255, 255), (x, cy), radius)
            pygame.draw.circle(surface, (190, 190, 200), (x, cy), radius, width=2)
