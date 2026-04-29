# Crea una aplicación Flask con rutas para mostrar, agregar, completar,
# editar y eliminar tareas, con persistencia en un archivo JSON.
#

import json
import os

from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# Ruta del archivo donde se guardarán las tareas
RUTA_ARCHIVO_TAREAS = os.path.join(os.path.dirname(__file__), "tareas.json")

# Lista global de tareas: cada tarea será un diccionario
# con las claves: "id", "texto" y "completada"
tareas = []
ultimo_id = 0


def cargar_tareas() -> None:
    """
    Carga las tareas desde el archivo JSON, si existe.
    Actualiza las variables globales tareas y ultimo_id.
    """
    global tareas, ultimo_id

    if not os.path.exists(RUTA_ARCHIVO_TAREAS):
        tareas = []
        ultimo_id = 0
        return

    try:
        with open(RUTA_ARCHIVO_TAREAS, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        tareas = []
        ultimo_id = 0
        return

    tareas = data.get("tareas", [])
    ultimo_id = data.get("ultimo_id", 0)


def guardar_tareas() -> None:
    """
    Guarda las tareas actuales y el último id en el archivo JSON.
    """
    data = {
        "tareas": tareas,
        "ultimo_id": ultimo_id,
    }
    try:
        with open(RUTA_ARCHIVO_TAREAS, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        # Si falla el guardado, simplemente se ignora para no romper la app.
        pass


# Cargar las tareas al iniciar la aplicación
cargar_tareas()


def agregar_tarea(texto: str) -> dict:
    """
    Agrega una nueva tarea con un id incremental.
    Devuelve la tarea creada.
    """
    global ultimo_id
    ultimo_id += 1
    tarea = {
        "id": ultimo_id,
        "texto": texto,
        "completada": False,
    }
    tareas.append(tarea)
    return tarea


def completar_tarea(tarea_id: int) -> bool:
    """
    Marca como completada la tarea con el id dado.
    Devuelve True si la encontró y actualizó, False en caso contrario.
    """
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["completada"] = True
            return True
    return False


def eliminar_tarea(tarea_id: int) -> bool:
    """
    Elimina la tarea con el id dado.
    Devuelve True si la encontró y eliminó, False en caso contrario.
    """
    global tareas

    for indice, tarea in enumerate(tareas):
        if tarea["id"] == tarea_id:
            tareas.pop(indice)
            return True
    return False


def editar_tarea(tarea_id: int, nuevo_texto: str) -> bool:
    """
    Cambia el texto de la tarea con el id dado.
    Devuelve True si la encontró y actualizó, False en caso contrario.
    """
    for tarea in tareas:
        if tarea["id"] == tarea_id:
            tarea["texto"] = nuevo_texto
            return True
    return False


# Ruta principal para mostrar tareas en la plantilla HTML
@app.route('/', methods=['GET'])
def mostrar_tareas():
    """
    Muestra la página principal con las tareas separadas
    en pendientes y completadas, junto con los contadores.
    """
    tareas_pendientes = [t for t in tareas if not t.get("completada")]
    tareas_completadas = [t for t in tareas if t.get("completada")]

    total_pendientes = len(tareas_pendientes)
    total_completadas = len(tareas_completadas)
    total_tareas = total_pendientes + total_completadas

    return render_template(
        "index.html",
        tareas_pendientes=tareas_pendientes,
        tareas_completadas=tareas_completadas,
        total_pendientes=total_pendientes,
        total_completadas=total_completadas,
        total_tareas=total_tareas,
    )


# Ruta para agregar una nueva tarea
@app.route('/agregar', methods=['POST'])
def ruta_agregar_tarea():
    data = request.form
    texto = data.get("texto", "").strip()
    if not texto:
        return redirect(url_for('mostrar_tareas'))
    agregar_tarea(texto)
    guardar_tareas()
    return redirect(url_for('mostrar_tareas'))


# Ruta para marcar una tarea como completada
@app.route('/completar/<int:tarea_id>', methods=['POST'])
def ruta_completar_tarea(tarea_id):
    exito = completar_tarea(tarea_id)
    if exito:
        guardar_tareas()
    return redirect(url_for('mostrar_tareas'))


# Ruta para eliminar una tarea
@app.route('/eliminar/<int:tarea_id>', methods=['POST'])
def ruta_eliminar_tarea(tarea_id):
    exito = eliminar_tarea(tarea_id)
    if exito:
        guardar_tareas()
    return redirect(url_for('mostrar_tareas'))


# Ruta para editar el texto de una tarea
@app.route('/editar/<int:tarea_id>', methods=['POST'])
def ruta_editar_tarea(tarea_id):
    nuevo_texto = request.form.get("texto", "").strip()
    if nuevo_texto:
        exito = editar_tarea(tarea_id, nuevo_texto)
        if exito:
            guardar_tareas()
    return redirect(url_for('mostrar_tareas'))


if __name__ == '__main__':
    app.run(debug=True)