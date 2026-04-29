# HackOps Simulator

Juego de escritorio en Python + Pygame con estetica terminal cyberpunk.

## Estructura

- `main.py` -> ciclo principal, estados de pantalla y eventos
- `ui.py` -> render de menu/terminal/end screens, cursor blink, historial visual
- `commands.py` -> parser y ejecucion de comandos del jugador
- `game_logic.py` -> misiones, progreso, alertas, probabilidades de exploit
- `persistence.py` -> guardado/carga JSON local
- `audio.py` -> efectos de sonido sinteticos
- `models.py` -> dataclasses de mision y progreso
- `settings.py` -> constantes visuales y configuracion global

## Ejecutar

```powershell
cd c:\Devjose\hackops_simulator
python main.py
```

## Requisitos

- Python 3.10+ (en Python 3.14 se recomienda `pygame-ce`)
- Dependencia:

```powershell
python -m pip install pygame-ce
```

## Build .exe (PyInstaller)

```powershell
cd c:\Devjose\hackops_simulator
python -m PyInstaller --noconfirm --clean --onefile --windowed --name HackOpsSimulator main.py
```

Resultado:

- `dist\HackOpsSimulator.exe`

## Comandos del juego

- `help`
- `scan [ip]`
- `connect [ip]`
- `exploit [servicio]`
- `ls`
- `cat [archivo]`
- `clear`

## Notas

- El juego es simulacion de hacking etico. No realiza hacking real.
- El progreso se guarda en `savegame.json`.
- El icono de la app se genera automaticamente en `assets/hackops_icon.png`.
