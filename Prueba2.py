# Crear una lista con los cuadrados de los n primeros numeros naturales
# Juego básico: Adivina el número (con contador de intentos)

import random

def juego_adivina_numero():
    numero_secreto = random.randint(1, 100)
    intentos = 0  # Contador de intentos
    print("¡Bienvenido al juego de adivinar el número!")
    print("Estoy pensando en un número entre 1 y 100.")
    while True:
        try:
            intento = int(input("Adivina el número: "))
            intentos += 1  # Sumar 1 intento cada vez que el jugador intente adivinar
            if intento < numero_secreto:
                print("Demasiado bajo. Intenta de nuevo.")
            elif intento > numero_secreto:
                print("Demasiado alto. Intenta de nuevo.")
            else:
                print(f"¡Correcto! Has adivinado el número en {intentos} intentos.")
                break
        except ValueError:
            print("Por favor, introduce un número válido.")

juego_adivina_numero()
