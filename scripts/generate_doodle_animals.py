from pathlib import Path
import pygame

ANIMALS: dict[int, tuple[str, str]] = {
    0: (
        "fly",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Fly: Score 0 -->
  <!-- Back legs -->
  <path d="M 170 330 Q 140 370 125 410" />
  <path d="M 330 330 Q 360 370 375 410" />
  <path d="M 185 350 Q 170 410 180 435" />
  <path d="M 315 350 Q 330 410 320 435" />
  <!-- Body -->
  <ellipse cx="250" cy="330" rx="90" ry="75" fill="#ffffff" />
  <!-- Wings -->
  <path d="M 215 260 C 130 190 120 100 195 90 C 240 85 245 180 235 250 Z" fill="#ffffff" />
  <path d="M 285 260 C 370 190 380 100 305 90 C 260 85 255 180 265 250 Z" fill="#ffffff" />
  <!-- Head -->
  <circle cx="250" cy="225" r="85" fill="#ffffff" />
  <!-- Antennae with round tips -->
  <path d="M 225 145 Q 200 95 180 110" />
  <circle cx="178" cy="112" r="12" fill="#141419" stroke="none" />
  <path d="M 275 145 Q 300 95 320 110" />
  <circle cx="322" cy="112" r="12" fill="#141419" stroke="none" />
  <!-- Cute Happy Eyes (^ ^) -->
  <path d="M 195 215 C 195 185 225 185 225 215" stroke-width="16" />
  <path d="M 275 215 C 275 185 305 185 305 215" stroke-width="16" />
  <!-- Cute Smile -->
  <circle cx="250" cy="238" r="8" fill="#141419" stroke="none" />
  <path d="M 235 250 Q 250 268 265 250" stroke-width="12" />
</svg>""",
    ),
    1: (
        "bunny",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Bunny: Score 1 -->
  <!-- Long Rounded Ears -->
  <path d="M 200 180 C 170 110 160 35 205 35 C 240 35 235 110 220 175 Z" fill="#ffffff" />
  <path d="M 280 175 C 265 110 260 35 295 35 C 340 35 330 110 300 180 Z" fill="#ffffff" />
  <!-- Body with paws -->
  <path d="M 160 350 L 160 435 Q 160 455 185 455 Q 210 455 210 435 L 210 410 L 290 410 L 290 435 Q 290 455 315 455 Q 340 455 340 435 L 340 350 Q 340 280 160 280 Z" fill="#ffffff" />
  <!-- Head -->
  <ellipse cx="250" cy="225" rx="125" ry="110" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 195 210 C 195 180 225 180 225 210" stroke-width="16" />
  <path d="M 275 210 C 275 180 305 180 305 210" stroke-width="16" />
  <!-- Nose and Mouth -->
  <path d="M 242 225 Q 250 220 258 225 Q 262 238 250 245 Q 238 238 242 225 Z" fill="#141419" stroke="none" />
  <path d="M 250 245 L 250 255" />
  <path d="M 230 252 Q 240 268 250 260 Q 260 268 270 252" />
  <!-- Whiskers -->
  <path d="M 180 235 L 130 230" stroke-width="10" />
  <path d="M 180 248 L 135 255" stroke-width="10" />
  <path d="M 320 235 L 370 230" stroke-width="10" />
  <path d="M 320 248 L 365 255" stroke-width="10" />
</svg>""",
    ),
    2: (
        "frog",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Frog: Score 2 -->
  <!-- Sitting legs -->
  <path d="M 140 330 C 80 350 85 445 155 450 C 185 450 195 410 190 370" fill="#ffffff" />
  <path d="M 360 330 C 420 350 415 445 345 450 C 315 450 305 410 310 370" fill="#ffffff" />
  <!-- Body -->
  <ellipse cx="250" cy="360" rx="95" ry="85" fill="#ffffff" />
  <!-- Front feet -->
  <path d="M 205 380 L 195 440 Q 185 455 205 455 Q 220 455 215 440 L 220 390" fill="#ffffff" />
  <path d="M 295 380 L 305 440 Q 315 455 295 455 Q 280 455 285 440 L 280 390" fill="#ffffff" />
  <!-- Big Eyes Mounds on top -->
  <circle cx="180" cy="180" r="45" fill="#ffffff" />
  <circle cx="320" cy="180" r="45" fill="#ffffff" />
  <!-- Big Cute Pupils -->
  <circle cx="185" cy="180" r="18" fill="#141419" stroke="none" />
  <circle cx="180" cy="174" r="6" fill="#ffffff" stroke="none" />
  <circle cx="315" cy="180" r="18" fill="#141419" stroke="none" />
  <circle cx="310" cy="174" r="6" fill="#ffffff" stroke="none" />
  <!-- Wide Head -->
  <ellipse cx="250" cy="245" rx="135" ry="90" fill="#ffffff" />
  <!-- Big Warm Froggy Smile -->
  <path d="M 175 240 Q 250 305 325 240" stroke-width="16" />
  <!-- Rosy cheeks -->
  <circle cx="170" cy="245" r="10" fill="#141419" stroke="none" />
  <circle cx="330" cy="245" r="10" fill="#141419" stroke="none" />
</svg>""",
    ),
    3: (
        "duck",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Duck: Score 3 -->
  <!-- Cute Body -->
  <path d="M 150 340 L 150 435 Q 150 455 175 455 Q 200 455 200 435 L 200 405 L 260 405 L 260 435 Q 260 455 285 455 Q 310 455 310 435 L 310 370 Q 380 370 380 300 Q 320 280 280 270 L 190 270 Q 150 270 150 340 Z" fill="#ffffff" />
  <!-- Little Wing -->
  <path d="M 190 320 Q 230 310 260 345 Q 230 375 190 360 Z" fill="#ffffff" />
  <!-- Head -->
  <circle cx="230" cy="195" r="85" fill="#ffffff" />
  <!-- Beak -->
  <path d="M 285 190 C 360 190 360 230 285 230 Z" fill="#ffffff" />
  <!-- Happy Closed Eye (^) -->
  <path d="M 230 190 C 230 160 260 160 260 190" stroke-width="16" />
  <!-- Little Hair Tuft -->
  <path d="M 220 115 Q 230 85 245 95 Q 240 115 235 125" />
</svg>""",
    ),
    4: (
        "cat",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Cat: Score 4 -->
  <!-- Body and legs -->
  <path d="M 140 375 L 140 440 Q 140 460 165 460 Q 190 460 190 440 L 190 410 L 250 410 L 250 440 Q 250 460 275 460 Q 300 460 300 440 L 300 410 L 330 410 L 330 440 Q 330 460 355 460 Q 380 460 380 440 L 380 310 Q 380 270 340 270 L 190 270 Q 140 270 140 375 Z" fill="#ffffff" />
  <!-- Curled Tail -->
  <path d="M 375 320 C 435 300 455 210 405 195 C 385 190 385 215 395 225 C 420 250 395 325 365 340" fill="#ffffff" />
  <!-- Triangular Ears -->
  <path d="M 165 160 L 140 65 Q 165 60 215 110" fill="#ffffff" />
  <path d="M 335 160 L 360 65 Q 335 60 285 110" fill="#ffffff" />
  <!-- Head -->
  <ellipse cx="250" cy="220" rx="130" ry="110" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 195 200 C 195 170 225 170 225 200" stroke-width="16" />
  <path d="M 275 200 C 275 170 305 170 305 200" stroke-width="16" />
  <!-- Nose and Smiling Mouth -->
  <path d="M 242 215 Q 250 210 258 215 Q 262 225 250 232 Q 238 225 242 215 Z" fill="#141419" stroke="none" />
  <path d="M 250 232 L 250 245" />
  <path d="M 230 242 Q 240 258 250 250 Q 260 258 270 242" />
  <!-- Whiskers -->
  <path d="M 180 225 L 120 220" stroke-width="10" />
  <path d="M 180 238 L 125 245" stroke-width="10" />
  <path d="M 320 225 L 380 220" stroke-width="10" />
  <path d="M 320 238 L 375 245" stroke-width="10" />
</svg>""",
    ),
    5: (
        "dog",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Dog: Score 5 (Exact Match to User Reference) -->
  <!-- Body -->
  <path d="M 120 375 L 120 440 Q 120 460 145 460 Q 170 460 170 440 L 170 410 Q 170 405 175 405 L 235 405 Q 240 405 240 410 L 240 440 Q 240 460 265 460 Q 290 460 290 440 L 290 410 Q 290 405 295 405 L 320 405 Q 325 405 325 410 L 325 440 Q 325 460 350 460 Q 375 460 375 440 L 375 290 Q 375 270 340 270 L 180 270 Q 120 270 120 375 Z" fill="#ffffff" />
  <!-- Tail -->
  <path d="M 120 320 C 65 315 65 240 85 240 C 95 240 95 290 125 300" fill="#ffffff" />
  <!-- Back leg hint -->
  <path d="M 185 410 L 185 440 Q 185 455 200 455 Q 215 455 215 440 L 215 405" fill="#ffffff" />
  <!-- Head -->
  <ellipse cx="270" cy="220" rx="135" ry="120" fill="#ffffff" />
  <!-- Left Floppy Ear -->
  <path d="M 175 135 C 110 135 60 200 70 270 C 80 325 150 330 165 285 C 175 250 170 190 185 150" fill="#ffffff" />
  <!-- Right Floppy Ear -->
  <path d="M 365 135 C 430 135 480 200 470 270 C 460 325 390 330 375 285 C 365 250 370 190 355 150" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 205 200 C 205 170 235 170 235 200" stroke-width="16" />
  <path d="M 305 200 C 305 170 335 170 335 200" stroke-width="16" />
  <!-- Cute Rounded Nose -->
  <path d="M 252 215 Q 270 205 288 215 Q 295 235 270 248 Q 245 235 252 215 Z" fill="#141419" stroke="none" />
  <!-- Smiling Mouth -->
  <path d="M 270 245 L 270 262" stroke-width="14" />
  <path d="M 245 260 Q 255 280 270 275 Q 285 280 295 260" stroke-width="14" />
</svg>""",
    ),
    6: (
        "fox",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Fox: Score 6 -->
  <!-- Bushy Tail -->
  <path d="M 340 370 C 430 380 470 270 395 200 C 355 180 330 240 370 280 C 385 295 365 330 320 350" fill="#ffffff" />
  <!-- Body and legs -->
  <path d="M 130 375 L 130 440 Q 130 460 155 460 Q 180 460 180 440 L 180 410 L 240 410 L 240 440 Q 240 460 265 460 Q 290 460 290 440 L 290 410 L 320 410 L 320 440 Q 320 460 345 460 Q 370 460 370 440 L 370 310 Q 370 270 330 270 L 180 270 Q 130 270 130 375 Z" fill="#ffffff" />
  <!-- Big Pointed Ears -->
  <path d="M 180 150 L 140 50 Q 170 50 225 110" fill="#ffffff" />
  <path d="M 320 150 L 360 50 Q 330 50 275 110" fill="#ffffff" />
  <!-- Fox Head with wide cheeks -->
  <path d="M 155 190 C 150 140 350 140 345 190 C 355 240 280 285 250 290 C 220 285 145 240 155 190 Z" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 200 200 C 200 170 230 170 230 200" stroke-width="16" />
  <path d="M 270 200 C 270 170 300 170 300 200" stroke-width="16" />
  <!-- Black Nose -->
  <circle cx="250" cy="272" r="12" fill="#141419" stroke="none" />
</svg>""",
    ),
    7: (
        "sheep",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Sheep: Score 7 -->
  <!-- Four stubby legs -->
  <path d="M 160 370 L 160 440 Q 160 455 180 455 Q 200 455 200 440 L 200 390" fill="#ffffff" />
  <path d="M 230 370 L 230 440 Q 230 455 250 455 Q 270 455 270 440 L 270 390" fill="#ffffff" />
  <path d="M 300 370 L 300 440 Q 300 455 320 455 Q 340 455 340 440 L 340 390" fill="#ffffff" />
  <!-- Fluffy Cloud Body -->
  <path d="M 180 320 Q 130 300 135 250 Q 120 190 180 180 Q 200 120 270 130 Q 340 115 370 170 Q 425 185 415 250 Q 425 315 370 340 Q 380 400 310 400 Q 240 415 190 390 Q 140 380 180 320 Z" fill="#ffffff" />
  <!-- Head -->
  <ellipse cx="230" cy="245" rx="65" ry="75" fill="#ffffff" />
  <!-- Droopy Ears -->
  <path d="M 175 220 C 130 220 130 260 170 260" fill="#ffffff" />
  <path d="M 285 220 C 330 220 330 260 290 260" fill="#ffffff" />
  <!-- Little wool cap -->
  <path d="M 195 185 Q 230 160 265 185 Q 230 195 195 185 Z" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 195 240 C 195 220 215 220 215 240" stroke-width="14" />
  <path d="M 245 240 C 245 220 265 220 265 240" stroke-width="14" />
  <!-- Little Smile -->
  <path d="M 220 275 Q 230 288 240 275" stroke-width="12" />
</svg>""",
    ),
    8: (
        "horse",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Horse: Score 8 -->
  <!-- Body and legs -->
  <path d="M 130 375 L 130 440 Q 130 460 155 460 Q 180 460 180 440 L 180 410 L 240 410 L 240 440 Q 240 460 265 460 Q 290 460 290 440 L 290 410 L 320 410 L 320 440 Q 320 460 345 460 Q 370 460 370 440 L 370 300 Q 370 270 330 270 L 180 270 Q 130 270 130 375 Z" fill="#ffffff" />
  <!-- Tail -->
  <path d="M 130 320 C 80 340 70 420 110 435 C 100 390 110 350 135 340" fill="#ffffff" />
  <!-- Mane tufts -->
  <path d="M 310 120 C 350 140 360 210 330 270" stroke-width="16" />
  <!-- Ears -->
  <path d="M 270 125 L 285 55 Q 270 65 250 110" fill="#ffffff" />
  <path d="M 295 135 L 320 65 Q 305 75 285 120" fill="#ffffff" />
  <!-- Head and Muzzle -->
  <path d="M 320 280 C 320 210 295 140 250 130 C 220 130 170 160 160 200 C 150 235 185 260 220 255 L 245 280 Z" fill="#ffffff" />
  <!-- Happy Eye (^) -->
  <path d="M 230 190 C 230 165 255 165 255 190" stroke-width="16" />
  <!-- Nostril and smile -->
  <circle cx="185" cy="220" r="8" fill="#141419" stroke="none" />
  <path d="M 180 235 Q 200 248 215 235" stroke-width="12" />
</svg>""",
    ),
    9: (
        "lion",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Lion: Score 9 -->
  <!-- Body and legs -->
  <path d="M 150 375 L 150 440 Q 150 460 175 460 Q 200 460 200 440 L 200 410 L 260 410 L 260 440 Q 260 460 285 460 Q 310 460 310 440 L 310 410 L 330 410 L 330 440 Q 330 460 355 460 Q 380 460 380 440 L 380 320 Q 380 280 330 280 L 190 280 Q 150 280 150 375 Z" fill="#ffffff" />
  <!-- Fluffy round mane -->
  <circle cx="260" cy="215" r="145" fill="#ffffff" stroke-width="16" />
  <!-- Round ears -->
  <circle cx="160" cy="140" r="30" fill="#ffffff" />
  <circle cx="360" cy="140" r="30" fill="#ffffff" />
  <!-- Head -->
  <circle cx="260" cy="215" r="95" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 210 200 C 210 170 240 170 240 200" stroke-width="16" />
  <path d="M 280 200 C 280 170 310 170 310 200" stroke-width="16" />
  <!-- Nose and smiling mouth -->
  <path d="M 252 215 Q 260 208 268 215 Q 272 225 260 235 Q 248 225 252 215 Z" fill="#141419" stroke="none" />
  <path d="M 260 235 L 260 248" />
  <path d="M 240 245 Q 250 262 260 252 Q 270 262 280 245" />
  <!-- Whiskers -->
  <circle cx="230" cy="235" r="4" fill="#141419" stroke="none" />
  <circle cx="290" cy="235" r="4" fill="#141419" stroke="none" />
</svg>""",
    ),
    10: (
        "bear",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">
  <!-- Bear: Score 10 -->
  <!-- Big Gentle Body -->
  <path d="M 120 375 L 120 440 Q 120 460 145 460 Q 170 460 170 440 L 170 410 L 235 410 L 235 440 Q 235 460 260 460 Q 285 460 285 440 L 285 410 L 320 410 L 320 440 Q 320 460 345 460 Q 370 460 370 440 L 370 290 Q 370 270 340 270 L 180 270 Q 120 270 120 375 Z" fill="#ffffff" />
  <!-- Cute Tummy Patch -->
  <ellipse cx="250" cy="365" rx="70" ry="55" stroke-width="10" />
  <!-- Round Ears -->
  <circle cx="170" cy="130" r="36" fill="#ffffff" />
  <circle cx="350" cy="130" r="36" fill="#ffffff" />
  <!-- Head -->
  <ellipse cx="260" cy="215" rx="135" ry="115" fill="#ffffff" />
  <!-- Happy Eyes (^ ^) -->
  <path d="M 205 195 C 205 165 235 165 235 195" stroke-width="16" />
  <path d="M 285 195 C 285 165 315 165 315 195" stroke-width="16" />
  <!-- Big Bear Snout -->
  <ellipse cx="260" cy="235" rx="42" ry="30" fill="#ffffff" />
  <ellipse cx="260" cy="225" rx="16" ry="11" fill="#141419" stroke="none" />
  <path d="M 260 236 L 260 248" />
  <path d="M 245 248 Q 260 265 275 248" />
</svg>""",
    ),
}


def main() -> None:
    pygame.init()
    out_dir = Path("assets/images/animals")
    out_dir.mkdir(parents=True, exist_ok=True)

    for score, (name, svg_content) in ANIMALS.items():
        svg_file = out_dir / f"score_{score}_{name}.svg"
        png_file = out_dir / f"score_{score}_{name}.png"
        svg_file.write_text(svg_content.strip(), encoding="utf-8")
        surf = pygame.image.load_sized_svg(str(svg_file), (512, 512))
        pygame.image.save(surf, str(png_file))
        svg_file.unlink(missing_ok=True)  # keep clean, PNG only
        print(f"Generated score {score} ({name}) -> {png_file.name} ({surf.get_width()}x{surf.get_height()})")

    print("\nAll 11 doodle line art animals successfully generated!")


if __name__ == "__main__":
    main()
