README - security_scanner.py (Escáner de riesgos de seguridad)
Este script recorre una carpeta, detecta posibles secretos/tokens/cadenas de conexión/ips internas en archivos soportados y genera un reporte XLSX cifrado con contraseña.

Requisitos
1) Python
Necesitas Python 3.x.
2) Librerías Python (dependencias)
Instala las dependencias necesarias:

pip install msoffcrypto-tool openpyxl pdfplumber python-docx
Nota: el script intenta extraer texto desde .docx, .xlsx y .pdf.
Si no usas esos formatos, igualmente instala lo anterior para evitar errores por imports.

Cómo ejecutar
El script soporta estos parámetros:

--path: ruta de la carpeta a escanear (obligatorio)
--out: ruta del archivo reporte final cifrado .xlsx (obligatorio)
--password: contraseña para cifrar el .xlsx (obligatorio)
Ejemplo en PowerShell:

python .\security_scanner.py --path "C:\ruta\proyecto" --out "C:\ruta\reporte_cifrado.xlsx" --password "MiContraFuerte123"
Qué genera
Primero crea un archivo temporal: reporte_cifrado.temp.xlsx
Luego lo cifra y deja el archivo final en --out
Borra el .temp.xlsx automáticamente al terminar
Formatos soportados para escaneo
El script escanea archivos con estas extensiones:

{ .config, .xml, .json, .env, .ini, .txt, .log, .sql, .py, .js, .ts, .cs, .vb, .docx, .xlsx, .pdf, .bat, .ps1 }

Las carpetas excluidas por defecto son: { bin, obj, .git, node_modules, $RECYCLE.BIN }

Qué detecta (tipos de hallazgos)
En base a regex sobre el contenido extraído, detecta:

Secreto Expuesto (Alta)

Busca pares PASSWORD/PWD/SECRET/TOKEN/APIKEY/API_KEY/CONTRASENA/CONTRASEÑA/LOGIN/URL con valor real usando un patrón tipo KEY=valor o KEY: valor.
Conexión DB (Alta)

Detecta patrones tipo string de conexión (por ejemplo Server=..., Data Source=..., User ID=..., Password=..., etc.).
Token JWT / Bearer (Alta)

Detecta JWT (eyJ... . ...) y/o tokens tipo Bearer <token>.
IP Interna (Baja)

Detecta IPs privadas típicas (10.x.x.x, 192.168.x.x, 172.16-31.x.x).
Estructura del reporte XLSX
El reporte incluye columnas:

Archivo
Ext
Tipo de Riesgo
Detalle (Valor Encontrado)
Severidad (Alta/Media/Baja)
Uso recomendado (buenas prácticas)
Escanea antes de publicar o abrir PRs grandes.
Usa una contraseña robusta para el reporte cifrado.
Evita escanear directorios innecesarios (reduce tiempo y ruido).