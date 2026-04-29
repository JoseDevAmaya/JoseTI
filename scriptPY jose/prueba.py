import time
def temporizador(segundos):
    for restante in range(segundos, 0, -1):
        print(f"Tiempo restante: {restante} segundos")
        time.sleep(1)
    print("¡Tiempo terminado!")


print("Hola, Cursor")
for i in range(5):
    print(i)
# Ejemplo de uso del temporizador: 5 segundos
# Llama a la función temporizador con 5 segundos
# Crear una lista de números primos menores de 100
primos = []
for num in range(2, 100):
    es_primo = True
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            es_primo = False
            break
    if es_primo:
        primos.append(num)
print("Números primos menores de 100:", primos)
def saludo():

    print("Hola, soy un rey campeo")

saludo()
# Calcular el factorial de un número dado
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
print("El factorial de 5 es:", factorial(5))
#calcular el ultimo numero de la lista de numeros primos
def ultimo_numero(lista):
    return lista[-1]
print("El ultimo numero de la lista de numeros primos es:", ultimo_numero(primos))  

def suma_lista(lista: list[int]) -> int:
    return sum(lista)
print("La suma de la lista de numeros primos es:", suma_lista(primos))

def promedio_lista(lista: list[int]) -> float:
    return sum(lista) / len(lista)
print("El promedio de la lista de numeros primos es:", promedio_lista(primos))







