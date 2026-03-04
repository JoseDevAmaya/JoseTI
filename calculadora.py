#Recorrer números del 1 al 50. Si el número es múltiplo de 3, imprimir "Fizz"; de 5, imprimir "Buzz"; de ambos, "FizzBuzz"; si no, el número.
for numero in range(1, 51):  # Recorre los números del 1 al 50 (incluyendo el 1 y excluyendo el 51)
    if numero % 3 == 0 and numero % 5 == 0:  # Si el número es múltiplo de 3 y de 5 a la vez
        print("FizzBuzz")  # Imprime "FizzBuzz"
    elif numero % 3 == 0:  # Si el número es múltiplo solo de 3
        print("Fizz")  # Imprime "Fizz"
    elif numero % 5 == 0:  # Si el número es múltiplo solo de 5
        print("Buzz")  # Imprime "Buzz"
    else:
        print(numero)  # Si no es múltiplo de 3 ni de 5, imprime el propio número