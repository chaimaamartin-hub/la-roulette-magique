# La Roulette Magique 🎡

Un jeu ludo-éducatif en plein écran sous Windows conçu pour apprendre les lettres (majuscules/minuscules) et les chiffres (1 à 20) en français pour les jeunes enfants.

## ✨ Fonctionnalités

* **Graphismes Haute Résolution & Anti-Aliasing :** Rendu fluide et net adapté aux écrans 1080p, 1440p et 4K.
* **Variété Typographique :** Rotation automatique de polices Windows standards (`Segoe UI`, `Comic Sans MS`, `Calibri`, `Verdana`, `Trebuchet MS`) avec alignement typographique strict sur ligne de base.
* **Animations Soignées :** Entrée échelonnée fluide en courbe cubic ease-out, effet scintillant arc-en-ciel (HSV) lors des bonnes réponses et flash rouge lors des erreurs.
* **Audio & Voix Naturelles :** Voix générées par Gemini 3.8 Flash TTS avec prosodie bienveillante et expressive :
  * Voix féminine d'institutrice : `Aoede`
  * Voix masculine d'instituteur : `Puck`
  * Effets sonores d'encouragement et d'apprentissage doux (sans buzzers agressifs).
* **Progression Pédagogique :**
  * 10 manches par session.
  * Manches 1 à 4 : 3 symboles.
  * Manches 5 à 7 : 4 symboles.
  * Manches 8 à 10 : 5 symboles.
  * Score sur 10 avec système de récompense par étoiles.
* **Écran de Configuration :** Grille personnalisable de 72 symboles (26 majuscules, 26 minuscules, 20 chiffres) avec sauvegarde automatique dans `config.json`.
* **Contrôles Ergonomiques :** Contrôle à la souris et touche `Échap (ESC)` pour revenir au menu ou quitter.

## 🚀 Installation & Lancement

### 1. Prérequis
* Python 3.10+
* `pygame-ce`

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancement du jeu
```bash
# Plein écran natif (par défaut)
python main.py

# Mode fenêtré
python main.py --windowed --width 1280 --height 720
```

### 4. Compilation en exécutable autonome (.exe)
```bash
pyinstaller --noconfirm --onedir --windowed --name "LaRouletteMagique" --add-data "assets;assets" main.py
```
L'exécutable autonome est généré dans `dist/LaRouletteMagique/LaRouletteMagique.exe`.

## 🧪 Tests
Exécuter la suite complète de tests unitaires :
```bash
pytest -v
```

## 🎙️ Génération Audio Offline
Toutes les répliques sont pré-générées hors ligne dans `assets/audio/`. Pour régénérer le lot complet :
```bash
python scripts/generate_all_audio.py
```
