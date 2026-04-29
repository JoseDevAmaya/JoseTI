from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class MoveResult:
    total: int
    moved: int
    failed: int
    cancelled: bool


class MailMover:
    def __init__(self, logger) -> None:
        self.logger = logger

    def move_by_entry_ids(
        self,
        namespace: object,
        entry_ids: List[str],
        destination_folder: object,
        batch_size: int,
        pause_seconds: float,
        dry_run: bool,
        progress_callback: Callable[[int, int, int], None] | None = None,
        cancel_callback: Callable[[], bool] | None = None,
    ) -> MoveResult:
        total = len(entry_ids)
        moved = 0
        failed = 0
        cancelled = False

        for index, entry_id in enumerate(entry_ids, start=1):
            if cancel_callback and cancel_callback():
                cancelled = True
                self.logger.info("Movimiento cancelado por usuario.")
                break

            try:
                item = namespace.GetItemFromID(entry_id)
                if item is None:
                    failed += 1
                    self.logger.warning("Item no encontrado para EntryID=%s", entry_id)
                    continue
                if item.Class != 43:
                    self.logger.debug("Item omitido (no MailItem), EntryID=%s", entry_id)
                    continue

                if dry_run:
                    moved += 1
                else:
                    item.Move(destination_folder)
                    moved += 1
            except Exception as exc:
                failed += 1
                self.logger.error("Error moviendo EntryID=%s | %s", entry_id, exc)

            if progress_callback:
                progress_callback(index, moved, failed)

            if index % max(1, batch_size) == 0:
                time.sleep(max(0.0, pause_seconds))

        return MoveResult(total=total, moved=moved, failed=failed, cancelled=cancelled)

    def operation_summary(
        self,
        source_label: str,
        destination_label: str,
        month_label: str,
        total_detected: int,
        result: MoveResult,
        dry_run: bool,
    ) -> Dict[str, str]:
        return {
            "source": source_label,
            "destination": destination_label,
            "month": month_label,
            "total_detected": str(total_detected),
            "moved": str(result.moved),
            "failed": str(result.failed),
            "cancelled": str(result.cancelled),
            "mode": "DRY-RUN" if dry_run else "MOVE",
        }
