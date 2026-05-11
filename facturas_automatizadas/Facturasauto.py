import pdfplumber
import re
import os

carpeta = "facturas"

for archivo in os.listdir(carpeta):

    # Solo archivos PDF
    if archivo.lower().endswith(".pdf"):

        ruta = os.path.join(carpeta, archivo)

        print(f"\nProcesando: {archivo}")

        try:
            with pdfplumber.open(ruta) as pdf:
                texto = ""
                for page in pdf.pages:
                    texto += (page.extract_text() or "") + "\n"

            # =========================
            # ✅ DETECTAR IMPORTE REAL
            # =========================
            importe = "IMPORTE"

            for palabra_clave in ["total factura", "total", "importe"]:
                for linea in texto.split("\n"):
                    if palabra_clave in linea.lower():
                        match = re.search(r'(\d+[.,]\d{2})', linea)
                        if match:
                            importe = match.group(1).replace(",", ".")
                            break
                if importe != "IMPORTE":
                    break

            # =========================
            # ✅ DETECTAR FECHA
            # =========================
            fecha_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', texto)

            if fecha_match:
                fecha = fecha_match.group(1).replace("/", "-")
            else:
                fecha = "FECHA"

            # =========================
            # ✅ CREAR NUEVO NOMBRE
            # =========================
            nuevo_nombre = f"{importe}_{fecha}.pdf"
            nueva_ruta = os.path.join(carpeta, nuevo_nombre)

            # Evitar sobrescribir archivos duplicados
            contador = 1
            while os.path.exists(nueva_ruta):
                nuevo_nombre = f"{importe}_{fecha}_{contador}.pdf"
                nueva_ruta = os.path.join(carpeta, nuevo_nombre)
                contador += 1

            # Renombrar archivo
            os.rename(ruta, nueva_ruta)

            print(f"✅ Renombrado a: {nuevo_nombre}")

        except Exception as e:
            print(f"❌ Error con {archivo}: {e}")
