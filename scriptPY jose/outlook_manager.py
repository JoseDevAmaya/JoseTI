import win32com.client
import pythoncom
import time
from datetime import datetime

##############################################################
# CONFIGURACIÓN
##############################################################

BATCH_SIZE = 20
SLEEP_TIME = 1

##############################################################
# DETECCIÓN DE STORES (PRIMARY / ARCHIVE / PST)
##############################################################

def detect_stores(namespace):
    stores = []

    try:
        primary_store = namespace.DefaultStore
    except:
        primary_store = None

    for store in namespace.Stores:
        try:
            # ❌ Carpetas públicas
            if store.ExchangeStoreType == 2:
                continue

            # ✅ Buzón principal
            if primary_store and store.StoreID == primary_store.StoreID:
                stores.append({
                    "type": "PRIMARY",
                    "store": store
                })
                continue

            # ✅ Archivado en línea
            if store.ExchangeStoreType == 1:
                try:
                    if store.IsArchive:
                        stores.append({
                            "type": "ARCHIVE",
                            "store": store
                        })
                except:
                    pass
                continue

            # ✅ PST
            if store.IsDataFileStore and store.ExchangeStoreType == 3:
                stores.append({
                    "type": "PST",
                    "store": store
                })

        except:
            continue

    return stores

##############################################################
# OBTENER INBOX Y SENT DE CUALQUIER STORE
##############################################################

def get_inbox_and_sent(store):
    folders = {}

    try:
        folders["Inbox"] = store.GetDefaultFolder(6)  # Inbox
    except:
        folders["Inbox"] = None

    try:
        folders["Sent"] = store.GetDefaultFolder(5)   # Sent Items
    except:
        folders["Sent"] = None

    return folders

##############################################################
# OBTENER MESES DISPONIBLES EN UNA CARPETA
##############################################################

def get_available_months(folder):
    items = folder.Items

    try:
        items.Sort("[ReceivedTime]")
        first = items.GetFirst()
        last = items.GetLast()
    except:
        return None, []

    # ✅ Carpeta vacía
    if first is None or last is None:
        return None, []

    try:
        first_dt = datetime(
            first.ReceivedTime.year,
            first.ReceivedTime.month,
            first.ReceivedTime.day
        )
        last_dt = datetime(
            last.ReceivedTime.year,
            last.ReceivedTime.month,
            last.ReceivedTime.day
        )
    except:
        return None, []

    meses = []
    actual = first_dt.replace(day=1)

    while actual <= last_dt:
        meses.append(actual.strftime("%Y-%m"))
        if actual.month == 12:
            actual = actual.replace(year=actual.year + 1, month=1)
        else:
            actual = actual.replace(month=actual.month + 1)

    print("\nMeses disponibles:")
    for i, m in enumerate(meses, 1):
        print(f"{i}. {m}")

    sel = int(input("\n➡ Elige mes inicial: "))
    return meses[sel - 1], meses

##############################################################
# OBTENER CORREOS DE UN MES (RESTRICT)
##############################################################

def get_messages_for_month(folder, month):
    year, mon = map(int, month.split("-"))

    start = datetime(year, mon, 1)
    if mon == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, mon + 1, 1)

    start_str = start.strftime("%m/%d/%Y %H:%M %p")
    end_str = end.strftime("%m/%d/%Y %H:%M %p")

    items = folder.Items.Restrict(
        f"[ReceivedTime] >= '{start_str}' AND [ReceivedTime] < '{end_str}'"
    )

    items.Sort("[ReceivedTime]")

    mensajes = []
    for item in items:
        try:
            if item.Class == 43:  # MailItem
                mensajes.append(item)
        except:
            continue

    return mensajes

##############################################################
# MOVER CORREOS POR LOTES
##############################################################

def move_messages(messages, destination, label):
    total = len(messages)
    moved = 0

    print(f"\n🚀 Moviendo correos ({label})")
    print(f"Total: {total}")

    for msg in list(messages):
        try:
            msg.Move(destination)
            moved += 1
        except Exception as e:
            print(f"⚠ Error: {e}")

        if moved % BATCH_SIZE == 0:
            print(f"➡ Movidos {moved}/{total}")
            time.sleep(SLEEP_TIME)

    print(f"✅ COMPLETADO {moved}/{total}")

##############################################################
# MAIN – DISEÑO FINAL
##############################################################

def main():
    pythoncom.CoInitialize()

    print("\n==============================================")
    print(" OUTLOOK AUTO-MOVER (DISEÑO FINAL) ")
    print("==============================================\n")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    outlook.Logon("", "", False, False)

    print("✅ Outlook inicializado")

    stores = detect_stores(outlook)
    if not stores:
        print("❌ No se detectaron stores válidos.")
        return

    for s in stores:
        store = s["store"]
        store_type = s["type"]

        print("\n==============================================")
        print(f"📦 BUZÓN: {store_type}")
        print("==============================================")

        folders = get_inbox_and_sent(store)

        for name, folder in folders.items():
            if not folder:
                continue

            if store_type == "PRIMARY":
                print(f"\n📂 PRIMARY / {name} (automático)")
            else:
                print(f"\n📂 {store_type} / {name}")

            mes_inicial, meses = get_available_months(folder)
            if not meses:
                print("ℹ Carpeta sin correos.")
                continue

            start_index = meses.index(mes_inicial)

            for mes in meses[start_index:]:
                print(f"\n📅 Procesando {store_type} / {name} / {mes}")

                mensajes = get_messages_for_month(folder, mes)

                if mensajes:
                    move_messages(
                        mensajes,
                        folder,  # ⚠ destino de prueba
                        f"{store_type} {name} {mes}"
                    )
                else:
                    print("ℹ No hay correos en este mes.")

                resp = input("¿Continuar con el siguiente mes? (S/N): ").strip().upper()
                if resp != "S":
                    print("⏹ Proceso detenido por el usuario.")
                    return

    print("\n✅ PROCESO COMPLETADO")

##############################################################

if __name__ == "__main__":
    main()