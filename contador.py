#Crear un script que me devuelva el nombre de todos los archivos de un directorio
import os

def get_file_names(directory):
    # Definir extensiones de imágenes
    image_extensions = ('.ico', '.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff', '.jfif', '.apng', '.avif')
    # Nombres de archivos típicos de iconos/imágenes HTML (en minúsculas)
    icon_names_html = {'favicon.ico', 'favicon.png', 'icon.png', 'logo.svg', 'logo.png', 'icon.svg'}

    archivos = []
    for f in os.listdir(directory):
        nombre_bajo = f.lower()
        # Ignorar si es una imagen o está en la lista de nombres comunes de iconos
        if not (nombre_bajo.endswith(image_extensions) or nombre_bajo in icon_names_html):
            archivos.append(f)
    return archivos

print(get_file_names("."))