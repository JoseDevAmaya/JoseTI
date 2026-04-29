from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import pythoncom

from folder_selector import FolderSelector
from logger_manager import LoggerManager
from mail_analyzer import MailAnalyzer
from mail_mover import MailMover
from outlook_connector import OutlookConnector


class MainApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Outlook Auto-Mover Jose")
        self.root.geometry("920x700")

        self.logger_manager = LoggerManager()
        self.logger = self.logger_manager.logger
        self.connector = OutlookConnector(self.logger)
        self.analyzer = MailAnalyzer(self.logger)
        self.mover = MailMover(self.logger)

        self.namespace = None
        self.stores = []
        self.source_folder = None
        self.dest_folder = None
        self.month_counts = {}
        self.entry_ids = []
        self.cancel_event = threading.Event()
        self.gui_queue = queue.Queue()
        self.worker_thread = None

        self._build_ui()
        self._connect_outlook()
        self.root.after(150, self._process_gui_queue)

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 6}
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main,
            text="Outlook Auto-Mover Jose",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor=tk.W, **padding)

        self.status_var = tk.StringVar(value="Inicializando...")
        self.progress_var = tk.StringVar(value="Progreso: 0")
        self.source_var = tk.StringVar(value="No seleccionada")
        self.dest_var = tk.StringVar(value="No seleccionada")
        self.month_selected_var = tk.StringVar(value="")
        self.month_count_var = tk.StringVar(value="Correos del mes: 0")
        self.batch_size_var = tk.IntVar(value=100)
        self.pause_var = tk.DoubleVar(value=0.2)
        self.dry_run_var = tk.BooleanVar(value=True)

        frm_source = ttk.LabelFrame(main, text="1) Carpeta origen")
        frm_source.pack(fill=tk.X, **padding)
        ttk.Label(frm_source, textvariable=self.source_var).pack(anchor=tk.W, **padding)
        ttk.Button(
            frm_source, text="Seleccionar carpeta origen", command=self.select_source_folder
        ).pack(anchor=tk.W, **padding)

        frm_analysis = ttk.LabelFrame(main, text="2) Analisis de correos")
        frm_analysis.pack(fill=tk.BOTH, expand=True, **padding)
        ttk.Button(frm_analysis, text="Escanear carpeta origen", command=self.start_analysis).pack(
            anchor=tk.W, **padding
        )

        columns = ("month", "count")
        self.month_table = ttk.Treeview(frm_analysis, columns=columns, show="headings", height=10)
        self.month_table.heading("month", text="Mes (YYYY-MM)")
        self.month_table.heading("count", text="Cantidad")
        self.month_table.column("month", width=200, anchor=tk.W)
        self.month_table.column("count", width=120, anchor=tk.E)
        self.month_table.bind("<<TreeviewSelect>>", self._on_month_select)
        self.month_table.pack(fill=tk.BOTH, expand=True, **padding)

        frm_month = ttk.LabelFrame(main, text="3) Mes y destino")
        frm_month.pack(fill=tk.X, **padding)
        ttk.Label(frm_month, text="Mes seleccionado:").grid(row=0, column=0, sticky=tk.W, **padding)
        ttk.Label(frm_month, textvariable=self.month_selected_var).grid(
            row=0, column=1, sticky=tk.W, **padding
        )
        ttk.Label(frm_month, textvariable=self.month_count_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, **padding
        )
        ttk.Label(frm_month, textvariable=self.dest_var).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, **padding
        )
        ttk.Button(
            frm_month, text="Seleccionar carpeta destino", command=self.select_dest_folder
        ).grid(row=3, column=0, sticky=tk.W, **padding)

        frm_options = ttk.LabelFrame(main, text="4) Opciones de procesamiento")
        frm_options.pack(fill=tk.X, **padding)
        ttk.Label(frm_options, text="Tamano batch:").grid(row=0, column=0, sticky=tk.W, **padding)
        ttk.Spinbox(frm_options, from_=10, to=1000, increment=10, textvariable=self.batch_size_var).grid(
            row=0, column=1, sticky=tk.W, **padding
        )
        ttk.Label(frm_options, text="Pausa por batch (seg):").grid(
            row=0, column=2, sticky=tk.W, **padding
        )
        ttk.Spinbox(frm_options, from_=0.0, to=3.0, increment=0.1, textvariable=self.pause_var).grid(
            row=0, column=3, sticky=tk.W, **padding
        )
        ttk.Checkbutton(
            frm_options,
            text="Modo simulacion (dry run, no mueve correos)",
            variable=self.dry_run_var,
        ).grid(row=1, column=0, columnspan=4, sticky=tk.W, **padding)

        frm_run = ttk.LabelFrame(main, text="5) Ejecucion y estado")
        frm_run.pack(fill=tk.X, **padding)
        ttk.Button(frm_run, text="Ejecutar movimiento", command=self.start_move).pack(
            side=tk.LEFT, **padding
        )
        ttk.Button(frm_run, text="Cancelar proceso", command=self.cancel_process).pack(
            side=tk.LEFT, **padding
        )
        ttk.Label(frm_run, textvariable=self.progress_var).pack(side=tk.LEFT, **padding)
        ttk.Label(frm_run, textvariable=self.status_var).pack(side=tk.LEFT, **padding)

        self.log_text = tk.Text(main, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, **padding)

    def _connect_outlook(self) -> None:
        try:
            self.namespace = self.connector.connect()
            self.stores = self.connector.detect_stores()
            if not self.stores:
                raise RuntimeError("No se detectaron stores disponibles.")
            self.status_var.set("Outlook conectado.")
            self._append_log("Outlook conectado correctamente.")
        except Exception as exc:
            self.status_var.set("Error de conexion Outlook")
            self._append_log(str(exc))
            messagebox.showerror("Error", str(exc))

    def select_source_folder(self) -> None:
        if not self.stores:
            messagebox.showwarning("Outlook", "No hay stores cargados.")
            return
        folder = FolderSelector.pick_folder(self.root, self.stores, "Seleccionar carpeta origen", self.connector)
        if folder is None:
            return
        self.source_folder = folder
        self.source_var.set(f"Origen: {self.connector.folder_label(folder)}")
        self._append_log(f"Carpeta origen seleccionada: {self.connector.folder_label(folder)}")

    def select_dest_folder(self) -> None:
        if not self.stores:
            messagebox.showwarning("Outlook", "No hay stores cargados.")
            return
        folder = FolderSelector.pick_folder(self.root, self.stores, "Seleccionar carpeta destino", self.connector)
        if folder is None:
            return
        self.dest_folder = folder
        self.dest_var.set(f"Destino: {self.connector.folder_label(folder)}")
        self._append_log(f"Carpeta destino seleccionada: {self.connector.folder_label(folder)}")

    def start_analysis(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Proceso en curso", "Ya hay un proceso ejecutandose.")
            return
        if self.source_folder is None:
            messagebox.showwarning("Falta origen", "Selecciona la carpeta origen antes de analizar.")
            return
        self.cancel_event.clear()
        self.month_table.delete(*self.month_table.get_children())
        self.status_var.set("Analizando...")
        self.worker_thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self.worker_thread.start()

    def _analysis_worker(self) -> None:
        pythoncom.CoInitialize()
        try:
            counts = self.analyzer.analyze_months(
                self.source_folder,
                progress_callback=lambda scanned, total: self.gui_queue.put(
                    ("analysis_progress", scanned, total)
                ),
                cancel_callback=self.cancel_event.is_set,
            )
            self.gui_queue.put(("analysis_done", counts))
        except Exception as exc:
            self.logger.exception("Error durante analisis.")
            self.gui_queue.put(("error", f"Error durante analisis: {exc}"))
        finally:
            pythoncom.CoUninitialize()

    def _on_month_select(self, _event=None) -> None:
        selected = self.month_table.selection()
        if not selected:
            return
        month = self.month_table.item(selected[0], "values")[0]
        count = self.month_counts.get(month, 0)
        self.month_selected_var.set(month)
        self.month_count_var.set(f"Correos del mes: {count}")

    def start_move(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Proceso en curso", "Ya hay un proceso ejecutandose.")
            return
        if self.source_folder is None or self.dest_folder is None:
            messagebox.showwarning("Faltan carpetas", "Selecciona origen y destino.")
            return
        if not self.month_selected_var.get():
            messagebox.showwarning("Falta mes", "Selecciona un mes de la tabla.")
            return
        if not self._validate_folders_different():
            return

        month = self.month_selected_var.get()
        estimated = self.month_counts.get(month, 0)
        summary = (
            "Confirma la operacion:\n\n"
            f"Origen: {self.connector.folder_label(self.source_folder)}\n"
            f"Destino: {self.connector.folder_label(self.dest_folder)}\n"
            f"Mes: {month}\n"
            f"Correos estimados: {estimated}\n"
            f"Batch: {self.batch_size_var.get()} | Pausa: {self.pause_var.get()} seg\n"
            f"Modo: {'DRY RUN' if self.dry_run_var.get() else 'MOVER'}\n\n"
            "Esta accion puede tardar varios minutos y solo opera en Outlook local."
        )
        if not messagebox.askyesno("Confirmacion", summary):
            self._append_log("Operacion cancelada por usuario en confirmacion.")
            return

        self.cancel_event.clear()
        self.status_var.set("Preparando movimiento...")
        self.worker_thread = threading.Thread(target=self._move_worker, daemon=True)
        self.worker_thread.start()

    def _move_worker(self) -> None:
        pythoncom.CoInitialize()
        try:
            month = self.month_selected_var.get()
            entry_ids = self.analyzer.collect_entry_ids_for_month(
                self.source_folder,
                month,
                progress_callback=lambda scanned, total, found: self.gui_queue.put(
                    ("collect_progress", scanned, total, found)
                ),
                cancel_callback=self.cancel_event.is_set,
            )
            self.entry_ids = entry_ids

            if self.cancel_event.is_set():
                self.gui_queue.put(("cancelled",))
                return

            result = self.mover.move_by_entry_ids(
                self.namespace,
                entry_ids,
                self.dest_folder,
                batch_size=self.batch_size_var.get(),
                pause_seconds=self.pause_var.get(),
                dry_run=self.dry_run_var.get(),
                progress_callback=lambda processed, moved, failed: self.gui_queue.put(
                    ("move_progress", processed, len(entry_ids), moved, failed)
                ),
                cancel_callback=self.cancel_event.is_set,
            )

            summary = self.mover.operation_summary(
                source_label=self.connector.folder_label(self.source_folder),
                destination_label=self.connector.folder_label(self.dest_folder),
                month_label=month,
                total_detected=len(entry_ids),
                result=result,
                dry_run=self.dry_run_var.get(),
            )
            self.logger.info(
                (
                    "Resumen final | origen=%s | destino=%s | mes=%s | total=%s | "
                    "movidos=%s | fallidos=%s | cancelado=%s | modo=%s"
                ),
                summary["source"],
                summary["destination"],
                summary["month"],
                summary["total_detected"],
                summary["moved"],
                summary["failed"],
                summary["cancelled"],
                summary["mode"],
            )
            self.gui_queue.put(("move_done", summary))
        except Exception as exc:
            self.logger.exception("Error durante movimiento.")
            self.gui_queue.put(("error", f"Error durante movimiento: {exc}"))
        finally:
            pythoncom.CoUninitialize()

    def _validate_folders_different(self) -> bool:
        try:
            if str(self.source_folder.EntryID) == str(self.dest_folder.EntryID):
                messagebox.showerror("Validacion", "Origen y destino no pueden ser la misma carpeta.")
                return False
        except Exception:
            source = self.connector.folder_label(self.source_folder)
            dest = self.connector.folder_label(self.dest_folder)
            if source == dest:
                messagebox.showerror("Validacion", "Origen y destino no pueden ser la misma carpeta.")
                return False
        return True

    def cancel_process(self) -> None:
        self.cancel_event.set()
        self._append_log("Se solicito cancelacion del proceso.")
        self.status_var.set("Cancelando...")

    def _process_gui_queue(self) -> None:
        while True:
            try:
                msg = self.gui_queue.get_nowait()
            except queue.Empty:
                break

            kind = msg[0]
            if kind == "analysis_progress":
                _, scanned, total = msg
                self.progress_var.set(f"Analisis: {scanned}/{total}")
            elif kind == "analysis_done":
                _, counts = msg
                self.month_counts = counts
                for month, count in counts.items():
                    self.month_table.insert("", tk.END, values=(month, count))
                self.status_var.set("Analisis completado.")
                self._append_log(f"Analisis completado. Meses detectados: {len(counts)}")
                if not counts:
                    messagebox.showinfo("Analisis", "No se detectaron correos validos en la carpeta origen.")
            elif kind == "collect_progress":
                _, scanned, total, found = msg
                self.progress_var.set(f"Preparando IDs: {scanned}/{total} | encontrados={found}")
            elif kind == "move_progress":
                _, processed, total, moved, failed = msg
                self.progress_var.set(
                    f"Movimiento: {processed}/{total} | movidos={moved} | errores={failed}"
                )
            elif kind == "move_done":
                _, summary = msg
                self.status_var.set("Proceso finalizado.")
                final_text = (
                    "Resumen final:\n"
                    f"Modo: {summary['mode']}\n"
                    f"Origen: {summary['source']}\n"
                    f"Destino: {summary['destination']}\n"
                    f"Mes: {summary['month']}\n"
                    f"Total detectado: {summary['total_detected']}\n"
                    f"Movidos: {summary['moved']}\n"
                    f"Errores: {summary['failed']}\n"
                    f"Cancelado: {summary['cancelled']}"
                )
                self._append_log(final_text.replace("\n", " | "))
                messagebox.showinfo("Proceso completado", final_text)
            elif kind == "cancelled":
                self.status_var.set("Proceso cancelado.")
                self._append_log("Proceso cancelado por usuario.")
            elif kind == "error":
                _, err = msg
                self.status_var.set("Error.")
                self._append_log(err)
                messagebox.showerror("Error", err)

        self.root.after(150, self._process_gui_queue)

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{text}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def run(self) -> None:
        self.root.mainloop()
