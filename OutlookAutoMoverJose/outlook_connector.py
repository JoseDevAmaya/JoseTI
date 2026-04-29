from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pythoncom
import win32com.client


@dataclass
class StoreInfo:
    store_id: str
    name: str
    store_type: str
    root_folder: object


class OutlookConnector:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.namespace = None

    def connect(self) -> object:
        pythoncom.CoInitialize()
        try:
            app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = app.GetNamespace("MAPI")
            self.logger.info("Conexion a Outlook/MAPI establecida.")
            return self.namespace
        except Exception as exc:
            self.logger.exception("No se pudo conectar a Outlook.")
            raise RuntimeError(f"No se pudo conectar a Outlook: {exc}") from exc

    def detect_stores(self) -> List[StoreInfo]:
        if self.namespace is None:
            raise RuntimeError("Outlook no esta conectado.")

        stores_info: List[StoreInfo] = []
        primary_store_id: Optional[str] = None
        try:
            primary_store_id = self.namespace.DefaultStore.StoreID
        except Exception:
            self.logger.warning("No fue posible leer DefaultStore.")

        for store in self.namespace.Stores:
            try:
                root = store.GetRootFolder()
                store_id = str(store.StoreID)
                name = str(root.Name)
                store_type = self._classify_store(store, primary_store_id)
                stores_info.append(
                    StoreInfo(
                        store_id=store_id,
                        name=name,
                        store_type=store_type,
                        root_folder=root,
                    )
                )
            except Exception as exc:
                self.logger.warning("Error detectando store: %s", exc)

        self.logger.info("Stores detectados: %s", len(stores_info))
        return stores_info

    def _classify_store(self, store: object, primary_store_id: Optional[str]) -> str:
        try:
            if primary_store_id and str(store.StoreID) == str(primary_store_id):
                return "PRIMARY"
        except Exception:
            pass

        try:
            if store.IsDataFileStore:
                return "PST"
        except Exception:
            pass

        try:
            if store.ExchangeStoreType == 1:
                return "ARCHIVE"
        except Exception:
            pass

        return "OTHER"

    @staticmethod
    def folder_label(folder: object) -> str:
        try:
            return str(folder.FolderPath)
        except Exception:
            try:
                return str(folder.Name)
            except Exception:
                return "(carpeta desconocida)"

    def folder_map(self) -> Dict[str, object]:
        if self.namespace is None:
            return {}
        mapping: Dict[str, object] = {}
        for store in self.detect_stores():
            self._walk_folders(store.root_folder, mapping)
        return mapping

    def _walk_folders(self, folder: object, mapping: Dict[str, object]) -> None:
        try:
            entry_id = str(folder.EntryID)
            mapping[entry_id] = folder
        except Exception:
            return

        try:
            for subfolder in folder.Folders:
                self._walk_folders(subfolder, mapping)
        except Exception:
            return
