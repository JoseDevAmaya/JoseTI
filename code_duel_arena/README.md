# Code Duel Arena

Juego de escritorio en Python + Pygame donde compites contra una IA en duelos de trivia tecnica, debugging y retos de codigo.

## Caracteristicas

- Interfaz estilo terminal hacker (cyber/retro)
- Input dinamico por teclado con historial y cursor parpadeante
- Preguntas cargadas desde JSON (`data/questions.json`)
- Tipos de reto: `output`, `debug`, `complete`
- Combate en tiempo real (vida, tiempo, dano)
- IA oponente con dificultad variable por etapa
- Progresion por nivel, XP y reputacion
- Guardado local en JSON (`savegame.json`)
- Pantalla de `Game Over` y `Victory`
- Icono generado automaticamente en `assets/code_duel_icon.png`

## Estructura modular

- `main.py` - ciclo principal y estados del juego
- `ui.py` - interfaz, terminal, menu y pantallas finales
- `questions.py` - carga y validacion de preguntas
- `game_logic.py` - reglas de combate, progreso y nivel
- `ai.py` - comportamiento de la IA
- `persistence.py` - guardado/carga JSON
- `audio.py` - efectos de sonido sinteticos
- `settings.py` - configuracion global

## Ejecutar

```powershell
cd C:\Devjose\code_duel_arena
python -m pip install -r requirements.txt
python main.py
```

## Controles

- Menu: mouse
- En combate:
  - Responder: `A`, `B`, `C`, `D` + `Enter`
  - `hint` para ver pista
  - `help` para ayuda
  - `clear` limpia terminal
  - Historial: `UP` / `DOWN`

## Build a EXE (PyInstaller)

```powershell
cd C:\Devjose\code_duel_arena
python -m PyInstaller --noconfirm --clean --onefile --windowed --name CodeDuelArena --add-data "data;data" main.py
```

Resultado en:

- `dist\CodeDuelArena.exe`

## Nota

El juego es simulacion educativa y no ejecuta hacking real.
