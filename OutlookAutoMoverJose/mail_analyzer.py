from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List


class MailAnalyzer:
    def __init__(self, logger) -> None:
        self.logger = logger

    @staticmethod
    def _is_mail_item(item: object) -> bool:
        try:
            return item.Class == 43
        except Exception:
            return False

    def analyze_months(
        self,
        folder: object,
        progress_callback: Callable[[int, int], None] | None = None,
        cancel_callback: Callable[[], bool] | None = None,
    ) -> Dict[str, int]:
        month_counts: Dict[str, int] = defaultdict(int)
        items = folder.Items
        total_items = int(items.Count)
        scanned = 0

        self.logger.info("Inicia analisis carpeta: %s", self._safe_folder(folder))

        for item in items:
            if cancel_callback and cancel_callback():
                self.logger.info("Analisis cancelado por usuario.")
                break

            scanned += 1
            try:
                if not self._is_mail_item(item):
                    continue
                received = item.ReceivedTime
                if isinstance(received, datetime):
                    key = received.strftime("%Y-%m")
                    month_counts[key] += 1
            except Exception as exc:
                self.logger.debug("Error leyendo item en analisis: %s", exc)

            if progress_callback and scanned % 300 == 0:
                progress_callback(scanned, total_items)

        if progress_callback:
            progress_callback(scanned, total_items)
        return dict(sorted(month_counts.items()))

    def collect_entry_ids_for_month(
        self,
        folder: object,
        month_label: str,
        progress_callback: Callable[[int, int, int], None] | None = None,
        cancel_callback: Callable[[], bool] | None = None,
    ) -> List[str]:
        entry_ids: List[str] = []
        items = folder.Items
        total_items = int(items.Count)
        scanned = 0

        self.logger.info(
            "Recolectando EntryID | carpeta=%s | mes=%s",
            self._safe_folder(folder),
            month_label,
        )

        for item in items:
            if cancel_callback and cancel_callback():
                self.logger.info("Recoleccion cancelada por usuario.")
                break

            scanned += 1
            try:
                if not self._is_mail_item(item):
                    continue
                received = item.ReceivedTime
                if isinstance(received, datetime) and received.strftime("%Y-%m") == month_label:
                    entry_id = str(item.EntryID)
                    if entry_id:
                        entry_ids.append(entry_id)
            except Exception as exc:
                self.logger.debug("Error recolectando EntryID: %s", exc)

            if progress_callback and scanned % 300 == 0:
                progress_callback(scanned, total_items, len(entry_ids))

        if progress_callback:
            progress_callback(scanned, total_items, len(entry_ids))

        self.logger.info("EntryIDs recolectados para %s: %s", month_label, len(entry_ids))
        return entry_ids

    @staticmethod
    def _safe_folder(folder: object) -> str:
        try:
            return str(folder.FolderPath)
        except Exception:
            return str(folder)
