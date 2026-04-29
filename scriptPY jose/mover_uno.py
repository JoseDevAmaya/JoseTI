import win32com.client
import time

# Configuración básica para prueba
MAX_TO_MOVE = 1       # Mover solo 1 correo
BATCH_SIZE = 1        # De uno en uno

# Conectar a Outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Carpeta origen → Elementos eliminados (código 3)
origin_folder = outlook.GetDefaultFolder(3)

# Buscar la carpeta destino dentro del PST
dest_folder = None
for store in outlook.Stores:
    if store.DisplayName == "Archivo de datos de Outlook":   # ← nombre del PST
        root = store.GetRootFolder()
        for f in root.Folders:
            if f.Name == "TestMove":                        # ← carpeta donde vamos a mover
                dest_folder = f
                break

if dest_folder is None:
    print("❌ No se encontró el PST o la carpeta 'TestMove'.")
    exit()

items = origin_folder.Items
total = len(items)
print(f"✅ Correos detectados en Eliminados: {total}")

count = 0

while len(items) > 0 and count < MAX_TO_MOVE:
    try:
        mail = items[0]      # Tomar siempre el primer correo
        mail.Move(dest_folder)
        count += 1
    except Exception as e:
        print(f"⚠ Error moviendo correo: {e}")

    print(f"➡ Movido: {count}/{MAX_TO_MOVE}")
    time.sleep(1)

print("✅ PRUEBA TERMINADA. Revisa el PST en 'TestMove'.")