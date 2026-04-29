from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


"""
README / INSTRUCCIONES DE USO
=============================

Este script organiza los archivos de la carpeta donde se encuentra,
clasificándolos por tipo (imágenes, documentos, audio, vídeo, etc.).

USO BÁSICO
----------
1. Copia el archivo `organizador_core.py` dentro de la carpeta que quieras organizar.
2. Abre una terminal/PowerShell en esa carpeta.
   - En el Explorador de Windows: clic derecho en la carpeta -> "Abrir en Terminal" (o similar).
3. Ejecuta el script con Python:

   python organizador_core.py

4. El script moverá los archivos de esa carpeta a subcarpetas como:
   - imagenes\\imagenes
   - documentos\\pdf, documentos\\word, etc.
   - audio\\audio
   - videos\\videos
   - comprimidos\\comprimidos
   - codigo\\codigo
   - otros (para extensiones no reconocidas)
"""


@dataclass(frozen=True)
class MoveResult:
    moved: int
    skipped: int
    errors: int


def default_rules() -> dict[str, dict[str, list[str]]]:
    return {
        "imagenes": {
            "imagenes": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg", ".heic"],
        },
        "documentos": {
            "pdf": [".pdf"],
            "word": [".doc", ".docx", ".odt", ".rtf"],
            "excel": [".xls", ".xlsx", ".xlsm", ".csv", ".ods"],
            "powerpoint": [".ppt", ".pptx", ".odp"],
            "texto": [".txt", ".md"],
        },
        "audio": {
            "audio": [".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".wma"],
        },
        "videos": {
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".m4v"],
        },
        "comprimidos": {
            "comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz"],
        },
        "codigo": {
            "codigo": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".php", ".html", ".css", ".json", ".xml"],
        },
    }


def build_extension_map(
    rules: dict[str, dict[str, list[str]]],
) -> dict[str, tuple[str, str]]:
    ext_map: dict[str, tuple[str, str]] = {}
    for top, sub in rules.items():
        for subfolder, exts in sub.items():
            for ext in exts:
                ext_map[ext.lower()] = (top, subfolder)
    return ext_map


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def organize_folder(
    folder: Path,
    *,
    rules: dict[str, dict[str, list[str]]] | None = None,
    dry_run: bool = False,
    exclude_folders: set[str] | None = None,
    self_path: Path | None = None,
    on_log: callable | None = None,
) -> MoveResult:
    if rules is None:
        rules = default_rules()
    if exclude_folders is None:
        exclude_folders = set()

    folder = folder.expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Ruta inválida (no es carpeta): {folder}")

    ext_map = build_extension_map(rules)
    excluded = {name.lower() for name in exclude_folders}
    for top in rules.keys():
        excluded.add(top.lower())
    excluded.add("otros")

    moved = 0
    skipped = 0
    errors = 0

    for item in folder.iterdir():
        try:
            if item.is_dir():
                if item.name.lower() in excluded:
                    skipped += 1
                else:
                    skipped += 1
                continue

            if self_path is not None and item.resolve() == self_path.resolve():
                skipped += 1
                continue

            ext = item.suffix.lower()
            if ext in ext_map:
                top, subfolder = ext_map[ext]
                target_dir = folder / top / subfolder
            else:
                target_dir = folder / "otros"

            target_dir.mkdir(parents=True, exist_ok=True)
            dest = unique_destination(target_dir / item.name)

            if on_log is not None:
                on_log(f"{'[DRY]' if dry_run else '[MOVE]'} {item.name} -> {dest.relative_to(folder)}")

            if not dry_run:
                item.rename(dest)
            moved += 1
        except Exception as e:
            errors += 1
            if on_log is not None:
                on_log(f"[ERROR] {item.name}: {e}")

    return MoveResult(moved=moved, skipped=skipped, errors=errors)


if __name__ == "__main__":
    # Carpeta donde se encuentra este script
    current_folder = Path(__file__).parent
    print(f"Organizando carpeta: {current_folder}")

    result = organize_folder(
        current_folder,
        dry_run=False,          # Cambia a True para modo prueba (no mueve archivos)
        self_path=Path(__file__),
        on_log=print,
    )

    print("\nResumen:")
    print("  Movidos:", result.moved)
    print("  Saltados:", result.skipped)
    print("  Errores:", result.errors)
