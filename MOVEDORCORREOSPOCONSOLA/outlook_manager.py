import win32com.client
import time
import os
import sys
import logging
from datetime import datetime

##############################################################
# CONFIGURACION
##############################################################

BATCH_SIZE = 20
SLEEP_TIME = 1
MONTHS_PAGE_SIZE = 12
MAX_SUBJECT_LEN = 120
LOG_FILE = "outlook_auto_mover.log"

##############################################################
# LOGGING
##############################################################

def setup_logging():
    logger = logging.getLogger("OutlookAutoMover")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


logger = setup_logging()

##############################################################
# UTILIDADES
##############################################################

def safe_input(prompt):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\n\nOperacion cancelada por el usuario.")
        logger.warning("Operacion cancelada por el usuario con Ctrl+C")
        return None


def truncate_text(text, max_len=MAX_SUBJECT_LEN):
    if text is None:
        return ""
    text = str(text).replace("\n", " ").replace("\r", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def get_folder_label(folder):
    try:
        return folder.FolderPath
    except Exception:
        try:
            return folder.Name
        except Exception:
            return "(carpeta desconocida)"


def is_mail_item(item):
    try:
        return item.Class == 43  # olMail
    except Exception:
        return False


##############################################################
# DETECCION DE STORES
##############################################################

def detect_stores(namespace):
    stores = []

    try:
        primary_store = namespace.DefaultStore
    except Exception:
        primary_store = None

    for store in namespace.Stores:
        try:
            try:
                if store.ExchangeStoreType == 2:
                    continue
            except Exception:
                pass

            root = store.GetRootFolder()

            if primary_store:
                try:
                    if store.StoreID == primary_store.StoreID:
                        stores.append({
                            "type": "PRIMARY",
                            "root": root,
                            "store_id": store.StoreID
                        })
                        continue
                except Exception:
                    pass

            try:
                if store.ExchangeStoreType == 0:
                    try:
                        if store.IsPrimaryExchangeMailbox:
                            stores.append({
                                "type": "PRIMARY",
                                "root": root,
                                "store_id": store.StoreID
                            })
                            continue
                    except Exception:
                        pass

                    continue
            except Exception:
                pass

            try:
                if store.ExchangeStoreType == 1:
                    stores.append({
                        "type": "ARCHIVE",
                        "root": root,
                        "store_id": store.StoreID
                    })
                    continue
            except Exception:
                pass

            try:
                if store.IsDataFileStore:
                    stores.append({
                        "type": "PST",
                        "root": root,
                        "store_id": store.StoreID
                    })
                    continue
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Error detectando store: {e}")
            continue

    return stores


##############################################################
# LISTADO DE CARPETAS
##############################################################

def walk_folders(folder, store_index, counter, results, prefix=""):
    counter[0] += 1
    fid = f"{store_index}.{counter[0]}"

    results.append({
        "id": fid,
        "folder": folder
    })

    print(f"{fid} {prefix}{folder.Name}")

    try:
        for sub in folder.Folders:
            walk_folders(sub, store_index, counter, results, prefix + "  ")
    except Exception as e:
        logger.warning(f"No se pudo recorrer subcarpetas de {get_folder_label(folder)}: {e}")


def choose_folder(stores, title):
    print("\n==============================================")
    print(f"   {title}")
    print("==============================================")

    all_folders = []

    for i, store in enumerate(stores, start=1):
        print(f"\n[{i}] {store['type']}")
        print("-----------------------------------")

        counter = [0]
        results = []
        walk_folders(store["root"], i, counter, results)
        all_folders.extend(results)

    choice = safe_input("\n➡ Introduce el ID (ej: 1.3): ")
    if choice is None:
        return None

    choice = choice.strip()

    for item in all_folders:
        if item["id"] == choice:
            return item["folder"]

    print("❌ Carpeta invalida.")
    logger.warning(f"Carpeta invalida seleccionada: {choice}")
    return None


##############################################################
# ANALISIS POR MESES
##############################################################

def count_messages_by_month(folder):
    print("\nAnalizando correos por mes...\n")
    logger.info(f"Iniciando analisis de carpeta: {get_folder_label(folder)}")

    month_counts = {}

    try:
        items = folder.Items
        items.Sort("[ReceivedTime]", True)
    except Exception as e:
        logger.error(f"No se pudo acceder a Items en la carpeta {get_folder_label(folder)}: {e}")
        return None

    scanned = 0

    for item in items:
        scanned += 1
        try:
            if not is_mail_item(item):
                continue

            dt = item.ReceivedTime
            key = dt.strftime("%Y-%m")
            month_counts[key] = month_counts.get(key, 0) + 1

            if scanned % 2000 == 0:
                print(f"➡ Revisados {scanned} elementos...")
        except Exception:
            continue

    if not month_counts:
        return {}

    logger.info(f"Analisis completado. Meses detectados: {len(month_counts)}")
    return month_counts


def choose_month_paginated(months, month_counts):
    if not months:
        return None

    page = 0
    total_pages = (len(months) + MONTHS_PAGE_SIZE - 1) // MONTHS_PAGE_SIZE

    while True:
        start = page * MONTHS_PAGE_SIZE
        end = start + MONTHS_PAGE_SIZE
        current = months[start:end]

        print("\n==============================================")
        print(f"   MESES DISPONIBLES (Pag {page + 1}/{total_pages})")
        print("==============================================")

        for idx, month in enumerate(current, start=1):
            print(f"{idx}. {month} -> {month_counts[month]} correos")

        nav = []
        if page > 0:
            nav.append("'p' (anterior)")
        if page < total_pages - 1:
            nav.append("'n' (siguiente)")
        nav_text = ", ".join(nav) if nav else "sin mas paginas"

        choice = safe_input(f"\n➡ Elige numero (1-{len(current)}) o {nav_text}: ")
        if choice is None:
            return None

        choice = choice.strip().lower()

        if choice == "n" and page < total_pages - 1:
            page += 1
            continue
        if choice == "p" and page > 0:
            page -= 1
            continue
        if choice.isdigit():
            selected_idx = int(choice)
            if 1 <= selected_idx <= len(current):
                return current[selected_idx - 1]

        print("❌ Opcion invalida. Intenta de nuevo.")


def collect_message_ids_for_month(folder, month_label):
    logger.info(f"Recolectando correos del mes {month_label} sin Restrict()")

    try:
        items = folder.Items
        items.Sort("[ReceivedTime]", True)
    except Exception as e:
        logger.error(f"No se pudo acceder a Items en {get_folder_label(folder)}: {e}")
        return None

    message_ids = []
    scanned = 0

    for item in items:
        scanned += 1
        try:
            if not is_mail_item(item):
                continue

            dt = item.ReceivedTime
            if dt.strftime("%Y-%m") == month_label:
                entry_id = item.EntryID
                if entry_id:
                    message_ids.append(entry_id)

            if scanned % 2000 == 0:
                print(f"➡ Revisados {scanned} elementos | encontrados {len(message_ids)} del mes {month_label}")
        except Exception:
            continue

    logger.info(f"EntryIDs recolectados para {month_label}: {len(message_ids)}")
    return message_ids


##############################################################
# CONFIRMACION
##############################################################

def confirm_move(source_folder, destination_folder, month_label, total_messages):
    source_label = get_folder_label(source_folder)
    destination_label = get_folder_label(destination_folder)

    print("\n==============================================")
    print("        CONFIRMACION DE MOVIMIENTO")
    print("==============================================")
    print(f"Mes: {month_label}")
    print(f"Correos a mover: {total_messages}")
    print(f"Origen: {source_label}")
    print(f"Destino: {destination_label}")

    choice = safe_input("\n➡ ¿Deseas continuar? (s/n): ")
    if choice is None:
        return False

    return choice.strip().lower() == "s"


##############################################################
# MOVIMIENTO
##############################################################

def move_messages_by_entryid(namespace, entry_ids, destination_folder, month_label):
    total = len(entry_ids)
    moved = 0
    failed = 0

    print(f"\nMoviendo correos ({month_label})")
    print(f"Total detectado: {total}\n")

    logger.info(
        f"Inicio de movimiento | mes={month_label} | total={total} | destino={get_folder_label(destination_folder)}"
    )

    for idx, entry_id in enumerate(entry_ids, start=1):
        try:
            item = namespace.GetItemFromID(entry_id)

            if not item:
                failed += 1
                logger.error(f"ERROR | No se pudo recuperar item | EntryID={entry_id}")
                continue

            if not is_mail_item(item):
                logger.warning(f"OMITIDO | No es MailItem | EntryID={entry_id}")
                continue

            try:
                subject = truncate_text(item.Subject)
            except Exception:
                subject = "(sin asunto)"

            item.Move(destination_folder)
            moved += 1
            logger.info(f"MOVIDO | {month_label} | {subject}")

        except Exception as e:
            failed += 1
            logger.error(f"ERROR_MOVIENDO | EntryID={entry_id} | error={e}")

        if idx % BATCH_SIZE == 0:
            print(f"➡ Procesados {idx}/{total} | Movidos: {moved} | Fallidos: {failed}")
            time.sleep(SLEEP_TIME)

    print("\n==============================================")
    print("              PROCESO FINALIZADO")
    print("==============================================")
    print(f"Total detectado: {total}")
    print(f"Movidos: {moved}")
    print(f"Fallidos: {failed}")
    print(f"Log: {os.path.abspath(LOG_FILE)}")

    logger.info(
        f"Fin de movimiento | mes={month_label} | total={total} | movidos={moved} | fallidos={failed}"
    )

    return moved, failed


##############################################################
# MAIN
##############################################################

def main():
    print("\n==============================================")
    print("      OUTLOOK AUTO-MOVER JOSÉ")
    print("==============================================\n")

    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        print(f"❌ No se pudo abrir Outlook/MAPI: {e}")
        logger.error(f"No se pudo abrir Outlook/MAPI: {e}")
        return

    stores = detect_stores(outlook)

    if not stores:
        print("❌ No se detectaron stores validos.")
        logger.error("No se detectaron stores validos")
        return

    logger.info(f"Stores detectados: {len(stores)}")

    origen = choose_folder(stores, "SELECCIONA CARPETA ORIGEN")
    if origen is None:
        return

    month_counts = count_messages_by_month(origen)
    if month_counts is None:
        print("❌ No se pudo analizar la carpeta origen.")
        return

    if not month_counts:
        print("❌ No hay correos validos en la carpeta seleccionada.")
        logger.warning(f"No hay correos validos en la carpeta: {get_folder_label(origen)}")
        return

    months = sorted(month_counts.keys())
    mes = choose_month_paginated(months, month_counts)
    if mes is None:
        return

    destino = choose_folder(stores, "SELECCIONA CARPETA DESTINO")
    if destino is None:
        return

    try:
        if origen.EntryID == destino.EntryID:
            print("❌ Origen y destino no pueden ser la misma carpeta.")
            logger.warning("Origen y destino son la misma carpeta")
            return
    except Exception:
        if get_folder_label(origen) == get_folder_label(destino):
            print("❌ Origen y destino no pueden ser la misma carpeta.")
            logger.warning("Origen y destino coinciden por FolderPath")
            return

    message_ids = collect_message_ids_for_month(origen, mes)
    if message_ids is None:
        print("❌ No se pudieron preparar los correos del mes seleccionado.")
        return

    if not message_ids:
        print("❌ No se encontraron correos para el mes seleccionado.")
        logger.warning(f"No se encontraron correos para el mes: {mes}")
        return

    if not confirm_move(origen, destino, mes, len(message_ids)):
        print("\nOperacion cancelada por el usuario.")
        logger.info("Operacion cancelada por el usuario en la confirmacion")
        return

    move_messages_by_entryid(outlook, message_ids, destino, mes)


##############################################################

if __name__ == "__main__":
    main()