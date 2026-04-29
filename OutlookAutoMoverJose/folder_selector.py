from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional


class FolderSelector(tk.Toplevel):
    def __init__(self, master, stores, title: str, connector):
        super().__init__(master)
        self.title(title)
        self.geometry("760x520")
        self.connector = connector
        self.stores = stores
        self.selected_folder = None
        self._id_to_folder = {}

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="Seleccionar", command=self._confirm).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT)

        self._populate_tree()
        self.transient(master)
        self.grab_set()
        self.tree.focus_set()

    def _populate_tree(self) -> None:
        for store in self.stores:
            store_text = f"[{store.store_type}] {store.name}"
            root_id = self.tree.insert("", tk.END, text=store_text, open=True)
            self._add_folder_node(root_id, store.root_folder)

    def _add_folder_node(self, parent_node: str, folder: object) -> None:
        try:
            folder_id = str(folder.EntryID)
            label = folder.Name
        except Exception:
            return

        node = self.tree.insert(parent_node, tk.END, text=label, open=False)
        self._id_to_folder[node] = folder

        try:
            for subfolder in folder.Folders:
                self._add_folder_node(node, subfolder)
        except Exception:
            return

    def _confirm(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        node = selected[0]
        folder = self._id_to_folder.get(node)
        if folder is None:
            return
        self.selected_folder = folder
        self.destroy()

    @classmethod
    def pick_folder(cls, master, stores, title: str, connector) -> Optional[object]:
        dialog = cls(master, stores, title, connector)
        master.wait_window(dialog)
        return dialog.selected_folder
