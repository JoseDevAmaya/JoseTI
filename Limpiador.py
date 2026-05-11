import os
import shutil
import psutil
from send2trash import send2trash
from datetime import datetime

# ========================
# CONFIGURACIÓN
# ========================
DISCO_PRINCIPAL = "C:\\"
UMBRAL_DISCO = 10  # %

# ========================
# FUNCIONES
# ========================

def limpiar_temporales():
    rutas = [
        os.environ.get("TEMP"),
        "C:\\Windows\\Temp",
        os.path.expanduser("~\\AppData\\Local\\Temp")
    ]

    total_archivos = 0
    for ruta in rutas:
        if ruta and os.path.exists(ruta):
            for root, dirs, files in os.walk(ruta):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                        total_archivos += 1
                    except:
                        pass
    return total_archivos


def limpiar_navegadores():
    rutas = {
        "Chrome": os.path.expanduser(
            "~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache"
        ),
        "Edge": os.path.expanduser(
            "~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache"
        )
    }

    total = 0
    for navegador, ruta in rutas.items():
        if os.path.exists(ruta):
            try:
                shutil.rmtree(ruta)
                total += 1
            except:
                pass
    return total


def vaciar_papelera():
    try:
        send2trash("C:\\$Recycle.Bin")
        return True
    except:
        return False


def comprobar_disco():
    uso = psutil.disk_usage(DISCO_PRINCIPAL)
    libre = 100 - uso.percent
    alerta = libre < UMBRAL_DISCO
    return libre, alerta


def reporte_salud():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    procesos = []
    for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
        procesos.append(p.info)

    procesos_top = sorted(
        procesos,
        key=lambda x: x['memory_percent'] if x['memory_percent'] else 0,
        reverse=True
    )[:5]

    return cpu, ram, procesos_top


# ========================
# MAIN
# ========================

def main():
    print("🧹 Escoba-IT - Mantenimiento Preventivo")
    print(f"Fecha: {datetime.now()}\n")

    temp_limpiados = limpiar_temporales()
    nav_limpiados = limpiar_navegadores()
    papelera_ok = vaciar_papelera()

    libre, alerta = comprobar_disco()
    cpu, ram, procesos = reporte_salud()

    print("✅ LIMPIEZA")
    print(f"- Archivos temporales eliminados: {temp_limpiados}")
    print(f"- Caché navegadores limpiada: {nav_limpiados}")
    print(f"- Papelera vaciada: {'Sí' if papelera_ok else 'No'}\n")

    print("💽 DISCO")
    print(f"- Espacio libre: {libre:.2f}%")
    if alerta:
        print("⚠️ ALERTA: Espacio en disco crítico\n")

    print("📊 SALUD DEL SISTEMA")
    print(f"- CPU: {cpu}%")
    print(f"- RAM: {ram}%\n")

    print("🔥 Procesos que más RAM consumen:")
    for p in procesos:
        print(f"  {p['name']} - {p['memory_percent']:.2f}%")


if __name__ == "__main__":
    main()
