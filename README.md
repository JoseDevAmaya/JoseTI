## Proyectos de prueba en Python

Este repositorio contiene varios **scripts de práctica en Python**, cada uno enfocado en una idea distinta (juegos, utilidades y pequeños ejercicios lógicos).

### Requisitos

- **Python 3.10 o superior** (cualquier versión 3.x reciente funciona).
- No se usan librerías externas, solo la **biblioteca estándar de Python**:
  - `os`
  - `random`
  - `time`

Para comprobar tu versión:

```bash
python --version
```

### Cómo ejecutar los scripts

Sitúate en la carpeta del proyecto:

```bash
cd c:\Devjose
```

Y luego ejecuta el script que quieras probar, por ejemplo:

```bash
python contador.py
```

En Windows también puede ser necesario usar:

```bash
py contador.py
```

Sustituye `contador.py` por el nombre del archivo que quieras ejecutar.

---

### `contador.py` – Listar archivos de un directorio

- **Descripción**: Muestra una lista con los nombres de los archivos de un directorio, **ignorando iconos e imágenes típicas** (`.png`, `.jpg`, `.ico`, etc.).
- **Librerías usadas**: `os`.
- **Uso básico**:
  - Tal como está, lista los archivos del **directorio actual** (`"."`).
  - Puedes cambiar el directorio editando la llamada:
    - `print(get_file_names("C:\\ruta\\a\\tu\\carpeta"))`

**Ejecutar:**

```bash
python contador.py
```

---

### `Prueba2.py` – Juego: Adivina el número

- **Descripción**: El programa piensa un número entre 1 y 100 y tú tienes que adivinarlo. Cuenta los **intentos** que haces.
- **Librerías usadas**: `random`.
- **Cómo se juega**:
  - El script pide que escribas un número.
  - Te dirá si es **demasiado alto** o **demasiado bajo**.
  - Al acertar, muestra cuántos intentos necesitaste.

**Ejecutar:**

```bash
python Prueba2.py
```

---

### `impostor.py` – Juego del impostor (palabra secreta)

- **Descripción**: Juego avanzado donde:
  - Se elige una **palabra secreta** dentro de una categoría (Frutas, Animales, Lugares, Objetos o Deportes).
  - Recibes **pistas difíciles** (longitud de la palabra, número de vocales, pistas genéricas).
  - Tienes **3 rondas** para adivinar la palabra.
  - Luego aparecen 3 bots que votan por una palabra; uno de ellos es el **impostor** que elige una palabra al azar para confundirte.
- **Librerías usadas**: `random`.
- **Flujo del juego**:
  1. El programa muestra la categoría y varias pistas.
  2. Escribes tu intento de palabra en cada ronda.
  3. Te indica si alguna de tus letras está en la palabra secreta.
  4. Después de las rondas, los bots votan y debes señalar quién es el impostor (Bot 1, Bot 2 o Bot 3).

**Ejecutar:**

```bash
python impostor.py
```

---

### `calculadora.py` – Ejercicio FizzBuzz (1 al 50)

- **Descripción**: Recorre los números del 1 al 50 e imprime:
  - `"FizzBuzz"` si el número es múltiplo de 3 y de 5.
  - `"Fizz"` si solo es múltiplo de 3.
  - `"Buzz"` si solo es múltiplo de 5.
  - El número tal cual si no es múltiplo de ninguno.
- **Librerías usadas**: ninguna adicional.

**Ejecutar:**

```bash
python calculadora.py
```

---

### `prueba.py` – Varios ejemplos y utilidades

Este archivo junta **varios mini-ejemplos**:

- **Temporizador con cuenta atrás** (`temporizador(segundos)`):
  - Muestra los segundos restantes y espera 1 segundo entre cada mensaje usando `time.sleep(1)`.
- **Impresión de saludo y bucle inicial**:
  - Imprime `"Hola, Cursor"` y luego los números del 0 al 4.
- **Cálculo de números primos menores de 100**:
  - Genera una lista de todos los números primos menores de 100.
- **Funciones de utilidad**:
  - `saludo()`: muestra un saludo personalizado.
  - `factorial(n)`: calcula el factorial de `n` de forma recursiva.
  - `ultimo_numero(lista)`: devuelve el último elemento de una lista.
  - `suma_lista(lista: list[int]) -> int`: suma todos los elementos de la lista.
  - `promedio_lista(lista: list[int]) -> float`: calcula el promedio de los elementos.

Al ejecutar el script se imprimen:

- La lista de primos menores de 100.
- El resultado del factorial de 5.
- El último número de la lista de primos.
- La suma de los primos.
- El promedio de esa lista.

**Ejecutar:**

```bash
python prueba.py
```

---

### Notas finales

- Todos los scripts están pensados como **ejercicios de práctica**, por lo que se pueden modificar libremente para seguir aprendiendo.
- Si quieres agruparlos en un paquete más grande, se puede crear un menú principal que importe estas funciones y ofrezca elegir el juego o utilidad desde un solo programa.

