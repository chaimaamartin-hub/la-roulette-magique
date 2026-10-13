from pathlib import Path
import pygame

ANIMALS_SVG: dict[int, tuple[str, str]] = {
    0: (
        "fly",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Fly: Score 0 -->
  <ellipse cx="250" cy="290" rx="55" ry="75" fill="#ffffff"/>
  <circle cx="250" cy="205" r="42" fill="#ffffff"/>
  <!-- Eyes -->
  <circle cx="232" cy="195" r="18" fill="#ffffff"/>
  <circle cx="268" cy="195" r="18" fill="#ffffff"/>
  <circle cx="234" cy="197" r="7" fill="#141419"/>
  <circle cx="266" cy="197" r="7" fill="#141419"/>
  <!-- Smile -->
  <path d="M 242 224 Q 250 232 258 224"/>
  <!-- Antennae -->
  <path d="M 235 166 Q 220 140 210 148"/>
  <path d="M 265 166 Q 280 140 290 148"/>
  <circle cx="209" cy="149" r="4" fill="#141419"/>
  <circle cx="291" cy="149" r="4" fill="#141419"/>
  <!-- Wings -->
  <path d="M 215 250 C 130 160 160 80 235 125 C 245 165 230 220 215 250 Z" fill="#ffffff"/>
  <path d="M 195 155 Q 215 185 220 225"/>
  <path d="M 285 250 C 370 160 340 80 265 125 C 255 165 270 220 285 250 Z" fill="#ffffff"/>
  <path d="M 305 155 Q 285 185 280 225"/>
  <!-- Legs -->
  <path d="M 205 260 Q 170 240 150 265"/>
  <path d="M 295 260 Q 330 240 350 265"/>
  <path d="M 200 300 Q 160 305 145 335"/>
  <path d="M 300 300 Q 340 305 355 335"/>
  <path d="M 210 340 Q 175 365 165 400"/>
  <path d="M 290 340 Q 325 365 335 400"/>
</svg>""",
    ),
    1: (
        "bunny",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Bunny: Score 1 -->
  <!-- Ears -->
  <path d="M 200 190 C 175 110 170 40 215 45 C 240 50 235 120 220 185 Z" fill="#ffffff"/>
  <path d="M 195 125 C 190 80 200 65 210 70" stroke-width="3"/>
  <path d="M 280 185 C 265 120 260 50 285 45 C 330 40 325 110 300 190 Z" fill="#ffffff"/>
  <path d="M 290 70 C 300 65 310 80 305 125" stroke-width="3"/>
  <!-- Body -->
  <ellipse cx="250" cy="360" rx="95" ry="90" fill="#ffffff"/>
  <!-- Head -->
  <ellipse cx="250" cy="245" rx="75" ry="65" fill="#ffffff"/>
  <!-- Eyes -->
  <ellipse cx="220" cy="235" rx="9" ry="14" fill="#141419"/>
  <circle cx="218" cy="230" r="3" fill="#ffffff"/>
  <ellipse cx="280" cy="235" rx="9" ry="14" fill="#141419"/>
  <circle cx="278" cy="230" r="3" fill="#ffffff"/>
  <!-- Nose and mouth -->
  <polygon points="244,256 256,256 250,264" fill="#141419"/>
  <path d="M 250 264 Q 242 278 232 272"/>
  <path d="M 250 264 Q 258 278 268 272"/>
  <!-- Whiskers -->
  <path d="M 215 260 L 160 252"/>
  <path d="M 215 268 L 155 272"/>
  <path d="M 285 260 L 340 252"/>
  <path d="M 285 268 L 345 272"/>
  <!-- Paws -->
  <ellipse cx="215" cy="435" rx="30" ry="18" fill="#ffffff"/>
  <ellipse cx="285" cy="435" rx="30" ry="18" fill="#ffffff"/>
  <path d="M 225 320 Q 250 340 275 320" stroke-width="4"/>
</svg>""",
    ),
    2: (
        "frog",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Frog: Score 2 -->
  <!-- Eye mounds -->
  <circle cx="195" cy="180" r="38" fill="#ffffff"/>
  <circle cx="305" cy="180" r="38" fill="#ffffff"/>
  <circle cx="195" cy="180" r="14" fill="#141419"/>
  <circle cx="192" cy="176" r="4" fill="#ffffff"/>
  <circle cx="305" cy="180" r="14" fill="#141419"/>
  <circle cx="302" cy="176" r="4" fill="#ffffff"/>
  <!-- Body / Head -->
  <ellipse cx="250" cy="260" rx="105" ry="85" fill="#ffffff"/>
  <!-- Smile -->
  <path d="M 180 260 Q 250 315 320 260"/>
  <circle cx="180" cy="256" r="4" fill="#141419"/>
  <circle cx="320" cy="256" r="4" fill="#141419"/>
  <!-- Nostrils -->
  <circle cx="240" cy="235" r="3" fill="#141419"/>
  <circle cx="260" cy="235" r="3" fill="#141419"/>
  <!-- Sitting legs -->
  <path d="M 155 310 C 110 320 100 410 170 420 C 200 420 215 390 205 340" fill="#ffffff"/>
  <path d="M 345 310 C 390 320 400 410 330 420 C 300 420 285 390 295 340" fill="#ffffff"/>
  <!-- Feet -->
  <path d="M 160 420 Q 140 435 125 430"/>
  <path d="M 175 422 Q 170 442 160 442"/>
  <path d="M 340 420 Q 360 435 375 430"/>
  <path d="M 325 422 Q 330 442 340 442"/>
  <!-- Front hands -->
  <path d="M 220 335 L 210 410 Q 195 425 210 425"/>
  <path d="M 280 335 L 290 410 Q 305 425 290 425"/>
</svg>""",
    ),
    3: (
        "duck",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Duck: Score 3 -->
  <!-- Body -->
  <path d="M 200 250 C 140 270 120 370 220 395 C 310 415 370 380 380 310 C 385 270 340 295 300 270 Z" fill="#ffffff"/>
  <!-- Wing -->
  <path d="M 205 285 C 180 320 220 370 280 350 C 295 330 270 290 220 285" fill="#ffffff"/>
  <path d="M 230 315 Q 260 345 285 330" stroke-width="3"/>
  <!-- Head -->
  <circle cx="295" cy="180" r="55" fill="#ffffff"/>
  <!-- Eye -->
  <circle cx="280" cy="165" r="10" fill="#141419"/>
  <circle cx="277" cy="162" r="3" fill="#ffffff"/>
  <!-- Beak -->
  <path d="M 250 180 C 200 185 190 205 240 215 Z" fill="#ffffff"/>
  <!-- Tail feathers -->
  <path d="M 380 310 Q 420 280 405 260 Q 390 285 370 300"/>
  <!-- Feet -->
  <path d="M 230 395 L 220 440 L 195 445 M 220 440 L 220 450 M 220 440 L 240 445"/>
  <path d="M 280 395 L 285 440 L 265 445 M 285 440 L 290 450 M 285 440 L 305 445"/>
</svg>""",
    ),
    4: (
        "cat",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Cat: Score 4 -->
  <!-- Body -->
  <ellipse cx="250" cy="360" rx="90" ry="85" fill="#ffffff"/>
  <!-- Tail -->
  <path d="M 330 380 C 400 370 420 260 370 240 C 355 235 345 255 360 265 C 385 285 375 350 320 365"/>
  <!-- Head -->
  <circle cx="250" cy="220" r="75" fill="#ffffff"/>
  <!-- Ears -->
  <polygon points="190,175 160,85 220,150" fill="#ffffff"/>
  <polygon points="310,175 340,85 280,150" fill="#ffffff"/>
  <!-- Eyes -->
  <ellipse cx="220" cy="205" rx="10" ry="14" fill="#141419"/>
  <circle cx="218" cy="200" r="3" fill="#ffffff"/>
  <ellipse cx="280" cy="205" rx="10" ry="14" fill="#141419"/>
  <circle cx="278" cy="200" r="3" fill="#ffffff"/>
  <!-- Nose and mouth -->
  <polygon points="245,225 255,225 250,233" fill="#141419"/>
  <path d="M 250 233 Q 240 248 230 240"/>
  <path d="M 250 233 Q 260 248 270 240"/>
  <!-- Whiskers -->
  <path d="M 210 230 L 140 220"/>
  <path d="M 210 240 L 135 245"/>
  <path d="M 290 230 L 360 220"/>
  <path d="M 290 240 L 365 245"/>
  <!-- Paws -->
  <ellipse cx="215" cy="435" rx="25" ry="15" fill="#ffffff"/>
  <ellipse cx="285" cy="435" rx="25" ry="15" fill="#ffffff"/>
</svg>""",
    ),
    5: (
        "dog",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Dog: Score 5 -->
  <!-- Floppy Ears -->
  <path d="M 180 180 C 130 180 120 280 155 300 C 180 300 195 240 190 195 Z" fill="#ffffff"/>
  <path d="M 320 180 C 370 180 380 280 345 300 C 320 300 305 240 310 195 Z" fill="#ffffff"/>
  <!-- Body -->
  <ellipse cx="250" cy="360" rx="90" ry="85" fill="#ffffff"/>
  <!-- Head -->
  <circle cx="250" cy="215" r="75" fill="#ffffff"/>
  <!-- Eyes -->
  <circle cx="220" cy="195" r="10" fill="#141419"/>
  <circle cx="218" cy="192" r="3" fill="#ffffff"/>
  <circle cx="280" cy="195" r="10" fill="#141419"/>
  <circle cx="278" cy="192" r="3" fill="#ffffff"/>
  <!-- Snout / Nose -->
  <ellipse cx="250" cy="235" rx="35" ry="25" fill="#ffffff"/>
  <ellipse cx="250" cy="225" rx="14" ry="10" fill="#141419"/>
  <path d="M 250 235 L 250 248"/>
  <path d="M 250 248 Q 238 260 228 250"/>
  <path d="M 250 248 Q 262 260 272 250"/>
  <!-- Tongue -->
  <path d="M 244 254 C 244 275 256 275 256 254" fill="#ffffff"/>
  <!-- Wagging Tail -->
  <path d="M 325 360 C 390 350 415 310 395 285 C 385 280 380 295 385 305"/>
  <!-- Paws -->
  <ellipse cx="215" cy="435" rx="28" ry="16" fill="#ffffff"/>
  <ellipse cx="285" cy="435" rx="28" ry="16" fill="#ffffff"/>
</svg>""",
    ),
    6: (
        "fox",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Fox: Score 6 -->
  <!-- Bushy Tail -->
  <path d="M 320 380 C 420 390 460 280 390 220 C 350 200 330 250 365 300 C 375 320 350 350 310 365" fill="#ffffff"/>
  <path d="M 390 220 Q 370 250 390 270" stroke-width="4"/>
  <!-- Body -->
  <ellipse cx="240" cy="360" rx="80" ry="80" fill="#ffffff"/>
  <!-- Head (fox shape with wide cheeks) -->
  <path d="M 160 200 C 160 140 320 140 320 200 C 330 250 260 295 240 300 C 220 295 150 250 160 200 Z" fill="#ffffff"/>
  <!-- Big Ears -->
  <polygon points="175,160 140,60 215,135" fill="#ffffff"/>
  <polygon points="305,160 340,60 265,135" fill="#ffffff"/>
  <path d="M 160 115 L 185 145" stroke-width="3"/>
  <path d="M 320 115 L 295 145" stroke-width="3"/>
  <!-- Eyes (clever curved) -->
  <path d="M 200 210 Q 215 195 225 212" stroke-width="6"/>
  <path d="M 280 210 Q 265 195 255 212" stroke-width="6"/>
  <!-- Cute black nose -->
  <circle cx="240" cy="285" r="9" fill="#141419"/>
  <!-- Paws -->
  <ellipse cx="205" cy="435" rx="24" ry="15" fill="#ffffff"/>
  <ellipse cx="270" cy="435" rx="24" ry="15" fill="#ffffff"/>
</svg>""",
    ),
    7: (
        "sheep",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Sheep: Score 7 -->
  <!-- Fluffy Cloud Body -->
  <path d="M 180 320 Q 140 310 140 270 Q 130 220 180 210 Q 190 160 250 165 Q 300 155 330 195 Q 380 200 375 250 Q 385 300 345 325 Q 355 375 305 385 Q 260 405 215 385 Q 165 385 180 320 Z" fill="#ffffff"/>
  <!-- Head -->
  <ellipse cx="250" cy="275" rx="50" ry="60" fill="#ffffff"/>
  <!-- Fluffy wool on head -->
  <path d="M 220 225 Q 210 205 230 200 Q 250 190 270 200 Q 290 205 280 225 Z" fill="#ffffff"/>
  <!-- Droopy ears -->
  <ellipse cx="190" cy="260" rx="25" ry="14" fill="#ffffff"/>
  <ellipse cx="310" cy="260" rx="25" ry="14" fill="#ffffff"/>
  <!-- Eyes -->
  <circle cx="230" cy="265" r="7" fill="#141419"/>
  <circle cx="270" cy="265" r="7" fill="#141419"/>
  <!-- Nose/mouth -->
  <path d="M 245 295 Q 250 300 255 295"/>
  <path d="M 250 300 L 250 310"/>
  <!-- 4 dainty legs -->
  <rect x="190" y="380" width="16" height="55" rx="8" fill="#ffffff"/>
  <rect x="225" y="385" width="16" height="50" rx="8" fill="#ffffff"/>
  <rect x="265" y="385" width="16" height="50" rx="8" fill="#ffffff"/>
  <rect x="300" y="380" width="16" height="55" rx="8" fill="#ffffff"/>
</svg>""",
    ),
    8: (
        "horse",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Horse: Score 8 -->
  <!-- Body -->
  <path d="M 190 320 C 160 330 150 410 240 415 C 320 415 350 370 330 320 Z" fill="#ffffff"/>
  <!-- Flowing Tail -->
  <path d="M 160 340 C 130 370 120 420 145 440 C 150 420 145 380 175 355"/>
  <!-- Neck and Head -->
  <path d="M 310 320 C 315 260 300 210 290 170 C 270 140 220 150 200 185 C 190 205 210 230 235 225 L 245 280 C 248 310 220 320 200 325" fill="#ffffff"/>
  <!-- Ears -->
  <polygon points="275,155 285,100 260,140" fill="#ffffff"/>
  <polygon points="290,165 310,110 280,150" fill="#ffffff"/>
  <!-- Mane -->
  <path d="M 290 140 C 330 160 340 230 320 290"/>
  <path d="M 285 165 C 315 185 325 240 315 280"/>
  <path d="M 280 190 C 300 210 315 255 305 275"/>
  <!-- Eye -->
  <circle cx="245" cy="175" r="8" fill="#141419"/>
  <circle cx="243" cy="173" r="2" fill="#ffffff"/>
  <!-- Muzzle / Nostril -->
  <circle cx="210" cy="205" r="4" fill="#141419"/>
  <path d="M 205 218 Q 218 224 225 218"/>
  <!-- Legs -->
  <rect x="220" y="405" width="20" height="45" rx="8" fill="#ffffff"/>
  <rect x="270" y="405" width="20" height="45" rx="8" fill="#ffffff"/>
</svg>""",
    ),
    9: (
        "lion",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Lion: Score 9 -->
  <!-- Magnificent Mane -->
  <path d="M 250 100 C 170 100 140 160 140 230 C 140 310 180 350 250 350 C 320 350 360 310 360 230 C 360 160 330 100 250 100 Z" fill="#ffffff"/>
  <path d="M 200 115 Q 160 135 155 175"/>
  <path d="M 300 115 Q 340 135 345 175"/>
  <path d="M 145 220 Q 120 250 140 280"/>
  <path d="M 355 220 Q 380 250 360 280"/>
  <path d="M 160 300 Q 190 345 230 345"/>
  <path d="M 340 300 Q 310 345 270 345"/>
  <!-- Body -->
  <ellipse cx="250" cy="380" rx="75" ry="65" fill="#ffffff"/>
  <!-- Head -->
  <circle cx="250" cy="230" r="65" fill="#ffffff"/>
  <!-- Round ears -->
  <circle cx="190" cy="180" r="22" fill="#ffffff"/>
  <circle cx="310" cy="180" r="22" fill="#ffffff"/>
  <!-- Eyes -->
  <circle cx="225" cy="215" r="9" fill="#141419"/>
  <circle cx="223" cy="212" r="3" fill="#ffffff"/>
  <circle cx="275" cy="215" r="9" fill="#141419"/>
  <circle cx="273" cy="212" r="3" fill="#ffffff"/>
  <!-- Nose and Muzzle -->
  <polygon points="242,238 258,238 250,248" fill="#141419"/>
  <path d="M 250 248 L 250 258"/>
  <path d="M 250 258 Q 238 270 225 260"/>
  <path d="M 250 258 Q 262 270 275 260"/>
  <!-- Whiskers -->
  <circle cx="230" cy="254" r="2" fill="#141419"/>
  <circle cx="235" cy="258" r="2" fill="#141419"/>
  <circle cx="270" cy="254" r="2" fill="#141419"/>
  <circle cx="265" cy="258" r="2" fill="#141419"/>
  <!-- Paws -->
  <ellipse cx="215" cy="435" rx="26" ry="16" fill="#ffffff"/>
  <ellipse cx="285" cy="435" rx="26" ry="16" fill="#ffffff"/>
</svg>""",
    ),
    10: (
        "bear",
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" fill="none" stroke="#141419" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
  <!-- Bear: Score 10 -->
  <!-- Round Ears -->
  <circle cx="175" cy="165" r="32" fill="#ffffff"/>
  <circle cx="175" cy="165" r="16" fill="#ffffff" stroke-width="3"/>
  <circle cx="325" cy="165" r="32" fill="#ffffff"/>
  <circle cx="325" cy="165" r="16" fill="#ffffff" stroke-width="3"/>
  <!-- Big Gentle Body -->
  <ellipse cx="250" cy="365" rx="110" ry="95" fill="#ffffff"/>
  <!-- Tummy patch -->
  <ellipse cx="250" cy="375" rx="70" ry="60" stroke-width="3"/>
  <!-- Head -->
  <circle cx="250" cy="235" r="80" fill="#ffffff"/>
  <!-- Friendly Eyes -->
  <circle cx="215" cy="215" r="10" fill="#141419"/>
  <circle cx="212" cy="211" r="3" fill="#ffffff"/>
  <circle cx="285" cy="215" r="10" fill="#141419"/>
  <circle cx="282" cy="211" r="3" fill="#ffffff"/>
  <!-- Snout -->
  <ellipse cx="250" cy="255" rx="42" ry="32" fill="#ffffff"/>
  <ellipse cx="250" cy="245" rx="16" ry="11" fill="#141419"/>
  <path d="M 250 256 L 250 268"/>
  <path d="M 235 268 Q 250 282 265 268"/>
  <!-- Big Warm Paws -->
  <ellipse cx="195" cy="440" rx="36" ry="20" fill="#ffffff"/>
  <ellipse cx="305" cy="440" rx="36" ry="20" fill="#ffffff"/>
  <!-- Claws detail -->
  <path d="M 180 448 Q 180 455 178 456 M 195 450 Q 195 458 195 458 M 210 448 Q 210 455 212 456" stroke-width="3"/>
  <path d="M 290 448 Q 290 455 288 456 M 305 450 Q 305 458 305 458 M 320 448 Q 320 455 322 456" stroke-width="3"/>
</svg>""",
    ),
}


def build_and_verify_all() -> None:
    pygame.init()
    out_dir = Path("assets/images/animals")
    out_dir.mkdir(parents=True, exist_ok=True)

    for score, (name, svg_text) in ANIMALS_SVG.items():
        file_path = out_dir / f"score_{score}_{name}.svg"
        file_path.write_text(svg_text.strip(), encoding="utf-8")
        # Verify loading with pygame-ce load_sized_svg
        surf = pygame.image.load_sized_svg(str(file_path), (250, 250))
        assert surf.get_size() == (250, 250), f"Failed size for {name}"
        print(f"Verified [{score}/10] {name} -> {file_path.name} ({surf.get_width()}x{surf.get_height()})")

    print("\nAll 11 animal SVGs successfully generated and verified in Pygame!")


if __name__ == "__main__":
    build_and_verify_all()
