# Outlook Auto-Mover Jose

Herramienta de escritorio para Windows que organiza y mueve correos dentro de Outlook (perfil activo) por mes (`YYYY-MM`) usando COM (`win32com`) y procesamiento por lotes para mayor estabilidad en buzones grandes.

## Caracteristicas

- Deteccion automatica de stores de Outlook: `PRIMARY`, `PST`, `ARCHIVE` y otros.
- Seleccion visual de carpeta origen y carpeta destino mediante arbol de carpetas.
- Analisis de correos por mes sin usar `Restrict()`.
- Recoleccion de correos por `EntryID` y movimiento en lotes (`batch`) configurables.
- Modo simulacion (`dry run`) para validar sin mover correos.
- Cancelacion de procesos en curso.
- Validacion para impedir origen y destino iguales.
- Logging local en `outlook_auto_mover.log` (sin envio de datos fuera del equipo).

## Estructura

- `main.py`: punto de entrada.
- `main_app.py`: GUI y orquestacion del flujo.
- `outlook_connector.py`: conexion a Outlook y deteccion de stores.
- `folder_selector.py`: selector de carpetas en interfaz.
- `mail_analyzer.py`: analisis de meses y recoleccion de `EntryID`.
- `mail_mover.py`: movimiento por lotes y resumen final.
- `logger_manager.py`: configuracion de logger local.
- `requirements.txt`: dependencias Python.

## Requisitos

- Windows con Microsoft Outlook instalado y perfil activo.
- Python 3.10+ recomendado.
- Permisos para abrir Outlook en la sesion del usuario.

## Instalacion

1. Abre PowerShell en `C:\Devjose\OutlookAutoMoverJose`.
2. Crea y activa un entorno virtual (opcional pero recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instala dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecucion

```powershell
python main.py
```

## Flujo de uso

1. Selecciona carpeta origen.
2. Pulsa **Escanear carpeta origen**.
3. Selecciona un mes detectado.
4. Selecciona carpeta destino.
5. Ajusta `batch`, pausa y modo `dry run` segun corresponda.
6. Pulsa **Ejecutar movimiento** y confirma.
7. Revisa progreso y resumen final.

## Logging

El archivo `outlook_auto_mover.log` guarda:

- fecha/hora
- carpeta origen
- carpeta destino
- mes procesado
- cantidad detectada
- movidos, errores, cancelacion
- modo (`DRY-RUN` o `MOVE`)

## Empaquetar a EXE (PyInstaller)

1. Instalar PyInstaller:

```powershell
pip install pyinstaller
```

2. Compilar:

```powershell
pyinstaller --noconfirm --onefile --windowed --name "OutlookAutoMoverJose" main.py
```

3. Ejecutable generado en:

- `dist\OutlookAutoMoverJose.exe`

## Validacion recomendada en entorno controlado

- Ejecutar primero con `dry run` en carpetas de prueba.
- Probar en buzones con volumen alto (50k+ items) y medir tiempo por lote.
- Probar escenarios de error:
  - Outlook cerrado o sin perfil cargado.
  - carpeta destino no accesible.
  - cancelacion durante recoleccion y durante movimiento.
  - mensajes eliminados durante el proceso.
- Ajustar `batch` y `pausa` para cada entorno (ej. 100-200 y 0.2-0.5s).
- Validar que el log cumpla trazabilidad operativa antes de pasar a produccion.

## Seguridad operativa

- La aplicacion no envia informacion a internet.
- No modifica configuracion del sistema.
- Solo interactua con carpetas del perfil activo de Outlook.
- Muestra confirmacion previa antes de ejecutar movimiento real.
