# Juego del impostor avanzado: adivinar palabra secreta y descubrir al impostor entre los bots
import random

def generar_pista_mas_dificil(palabra, categoria):
    # Genera una pista menos obvia a partir de la palabra y la categoría.
    # Ejemplos de pistas genéricas y menos descriptivas.
    pistas_genericas = {
        "Frutas": [
            "Forma parte de una ensalada dulce.",
            "Puedes encontrarla en un puesto de mercado.",
            "Tiene semilla(s) en su interior.",
            "Algunos la prefieren en jugo.",
            "No crece en invierno.",
        ],
        "Animales": [
            "Tiene sentidos agudos.",
            "Es parte del reino animal.",
            "Puede moverse por sí solo.",
            "No es un ser humano.",
            "En algunos países es símbolo de algo.",
        ],
        "Lugares": [
            "Puedes encontrar personas ahí.",
            "Aparece en los mapas.",
            "No es ni demasiado grande ni demasiado pequeño.",
            "Algunos sueñan con visitarlo.",
            "Puede cambiar según la cultura.",
        ],
        "Objetos": [
            "A veces está cerca tuyo.",
            "Puede ayudarte en alguna tarea.",
            "No es comestible.",
            "Es parte de la vida diaria.",
            "Suele encontrarse en casas.",
        ],
        "Deportes": [
            "Se practica en grupo o individual.",
            "A veces se necesita equipo especial.",
            "Tiene reglas propias.",
            "No siempre se juega en interior.",
            "Implica actividad física.",
        ]
    }
    # Elegir una pista aleatoria de la categoría
    pista_base = random.choice(pistas_genericas.get(categoria, ["Es algo... pero no tan fácil de adivinar."]))
    # También podemos dar pistas sobre la cantidad de vocales o consonantes u otra característica sutil
    vocales = sum(1 for l in palabra if l in "aeiouáéíóú")
    consonantes = len(palabra) - vocales
    pista_extra = random.choice([
        f"Tiene {vocales} vocal(es) en su nombre.",
        f"Contiene {consonantes} consonante(s).",
        f"No comienza con la letra '{palabra[0] if len(palabra) else '?'}'.",
        "Su nombre no tiene números.",
    ])
    # Elegir aleatoriamente si dar la base o la extra
    return random.choice([pista_base, pista_extra])

def juego_del_impostor():
    categorias_palabras = {
        "Frutas": [
            {"palabra": "banana", "pista": "Es una fruta tropical amarilla, se usa mucho en batidos."},
            {"palabra": "manzana", "pista": "Fruta roja o verde, famosa en cuentos y es símbolo de Nueva York."},
            {"palabra": "pera", "pista": "Fruta jugosa, verde o amarilla, con forma de bombilla."},
            {"palabra": "melon", "pista": "Fruta grande y redonda, de pulpa naranja o verde, muy dulce en verano."},
            {"palabra": "uva", "pista": "Fruta pequeña que crece en racimos, base para hacer vino."},
        ],
        "Animales": [
            {"palabra": "perro", "pista": "Es un animal doméstico, el mejor amigo del hombre."},
            {"palabra": "raton", "pista": "Pequeño roedor, famoso en caricaturas y cuentos de laboratorio."},
            {"palabra": "tigre", "pista": "Felino grande, rayado, rey de la jungla en Asia."},
            {"palabra": "gato", "pista": "Animal doméstico que maúlla y caza ratones."},
            {"palabra": "pato", "pista": "Nada, vuela y hace cuac. Común en lagos y caricaturas."},
        ],
        "Lugares": [
            {"palabra": "montaña", "pista": "Elevación natural del terreno, famosa por los Andes y el Everest."},
            {"palabra": "playa", "pista": "Lugar favorito en verano, con arena y mar."},
            {"palabra": "bosque", "pista": "Gran extensión de árboles, hogar de muchos animales silvestres."},
            {"palabra": "ciudad", "pista": "Centro urbano con muchas personas, edificios y tráfico."},
            {"palabra": "pueblo", "pista": "Comunidad pequeña, menos habitantes que una ciudad."},
        ],
        "Objetos": [
            {"palabra": "luz", "pista": "Lo necesitas para ver, opuesto a la oscuridad."},
            {"palabra": "computadora", "pista": "Objeto electrónico para programar, jugar y navegar en internet."},
            {"palabra": "lapiz", "pista": "Escribes y dibujas con él antes de borrar."},
            {"palabra": "silla", "pista": "Mueble donde te sientas, normalmente tiene cuatro patas."},
            {"palabra": "mesa", "pista": "Donde comes o estudias, suele ir con sillas alrededor."},
        ],
        "Deportes": [
            {"palabra": "futbol", "pista": "Deporte más popular del mundo, Messi juega esto."},
            {"palabra": "tenis", "pista": "Se juega con raqueta y pelota amarilla, Nadal es estrella aquí."},
            {"palabra": "balon", "pista": "Elemento esencial en básquet, fútbol y voleibol."},
            {"palabra": "golf", "pista": "Deporte de palos, pelotitas, hoyos y campos verdes."},
            {"palabra": "rugby", "pista": "Deporte de contacto, parecido al fútbol americano, famosos los All Blacks."},
        ],
    }

    print("Bienvenido al juego del impostor\n")
    categoria = random.choice(list(categorias_palabras.keys()))
    lista_palabras = categorias_palabras[categoria]
    seleccion = random.choice(lista_palabras)
    palabra_secreta = seleccion['palabra']
    pista_real = seleccion['pista']  # No usaremos la pista real para el jugador

    print("Se ha seleccionado una palabra secreta.")
    print(f"Pista 1: La categoría es '{categoria}'.")
    pista_dificil = generar_pista_mas_dificil(palabra_secreta, categoria)
    print(f"Pista 2: {pista_dificil}")
    print(f"Pista 3: La palabra tiene {len(palabra_secreta)} letras.")
    print("Tienes 3 rondas para adivinar la palabra.\n")

    palabras_posibles = [
        p['palabra'] for p in lista_palabras if p['palabra'] != palabra_secreta
    ]
    if len(palabras_posibles) < 3:
        palabras_posibles = [
            p['palabra'] for sublist in categorias_palabras.values() for p in sublist if p['palabra'] != palabra_secreta
        ]

    rondas = 3
    acerto = False
    for ronda in range(1, rondas + 1):
        print(f"--- Ronda {ronda} ---")
        intento = input("Adivina la palabra: ").strip().lower()
        if intento == palabra_secreta:
            print(f"\n¡Correcto! Has adivinado la palabra secreta '{palabra_secreta}' en la ronda {ronda}.")
            acerto = True
            break
        else:
            letras_correctas = set([l for l in intento if l in palabra_secreta])
            if letras_correctas:
                print(f"Incorrecto. Algunas letras de tu intento están en la palabra: {', '.join(letras_correctas)}")
            else:
                print("Incorrecto. Ninguna letra de tu intento está en la palabra secreta.")
        print()

    print("\n¡Fin de las rondas!")
    print("\nAhora los bots van a votar su sospecha de palabra secreta y habrá un impostor que intenta confundirte.")
    print("Debes intentar descubrir cuál de los bots es el impostor.")

    bots = ["Bot 1", "Bot 2", "Bot 3"]
    impostor_index = random.randint(0, 2)

    palabras_voto = random.sample(palabras_posibles, 2)
    while True:
        palabra_impostor = random.choice([
            p['palabra']
            for sublist in categorias_palabras.values()
            for p in sublist
            if p['palabra'] != palabra_secreta and p['palabra'] not in palabras_voto
        ])
        if palabra_impostor:
            break

    votos_de_bots = []
    votos_de_bots.insert(impostor_index, palabra_impostor)
    bots_iter = iter(palabras_voto)
    for i in range(3):
        if i == impostor_index:
            continue
        palabra = next(bots_iter)
        votos_de_bots.insert(i, palabra)

    print("\nVotaciones de los bots:")
    for idx, voto in enumerate(votos_de_bots):
        print(f"{bots[idx]} vota que la palabra secreta es '{voto}'")
    print("\nUno de los bots es el impostor: eligió cualquier palabra para confundirte.")

    try:
        seleccion_usuario = int(input("¿Quién crees que es el impostor? (1, 2 o 3): ").strip()) - 1
        if seleccion_usuario == impostor_index:
            print("\n¡Correcto! Has detectado al impostor.")
        else:
            print(f"\nIncorrecto. El impostor era el {bots[impostor_index]}.")
    except ValueError:
        print(f"\nEntrada inválida. El impostor era el {bots[impostor_index]}.")

    if not acerto:
        print(f"\nNo lograste adivinar la palabra secreta, era: '{palabra_secreta}'. Mejor suerte la próxima.")

juego_del_impostor()