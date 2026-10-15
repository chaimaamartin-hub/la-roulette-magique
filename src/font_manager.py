from pathlib import Path
import pygame

WINDOWS_FONTS: list[str] = [
    "Segoe UI",
    "Comic Sans MS",
    "Calibri",
    "Verdana",
    "Trebuchet MS",
]


class FontManager:
    def __init__(self, font_pool: list[str] | None = None) -> None:
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_pool: list[str] = font_pool or list(WINDOWS_FONTS)
        self._cache: dict[tuple[str, int, bool], pygame.font.Font] = {}

    def get_font(self, font_name: str, size: int, bold: bool = False) -> pygame.font.Font:
        if size <= 0:
            raise ValueError(f"CRITICAL: Font size must be positive, got {size}.")
        key = (font_name, size, bold)
        if key in self._cache:
            return self._cache[key]

        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
        except Exception:
            font = pygame.font.Font(None, size)

        self._cache[key] = font
        return font

    def get_ui_font(self, size: int, bold: bool = True) -> pygame.font.Font:
        return self.get_font("Segoe UI", size, bold=bold)

    def get_title_font(self, size: int) -> pygame.font.Font:
        if size <= 0:
            raise ValueError(f"CRITICAL: Font size must be positive, got {size}.")
        available = pygame.font.get_fonts()
        for name in ["Trebuchet MS", "Segoe UI", "Bahnschrift"]:
            # Match system font name (ignoring spaces and casing)
            normalized = name.lower().replace(" ", "")
            if normalized in available or name.lower() in available:
                return self.get_font(name, size, bold=True)
        return self.get_ui_font(size, bold=True)

    def get_card_font(self, card_index: int, size: int) -> pygame.font.Font:
        font_name = self.font_pool[card_index % len(self.font_pool)]
        return self.get_font(font_name, size, bold=True)

    def get_round_font(self, round_index: int, size: int) -> pygame.font.Font:
        idx = max(0, round_index - 1)
        font_name = self.font_pool[idx % len(self.font_pool)]
        return self.get_font(font_name, size, bold=True)

    def get_cap_center_offset(self, font: pygame.font.Font) -> float:
        if font is None or not isinstance(font, pygame.font.Font):
            raise TypeError("CRITICAL: font must be a pygame.font.Font instance.")
        ref_surf = font.render("H", True, (0, 0, 0))
        bbox = ref_surf.get_bounding_rect()
        if bbox.height == 0:
            return float(ref_surf.get_height() / 2.0)
        return float((bbox.top + bbox.bottom - 1) / 2.0)

