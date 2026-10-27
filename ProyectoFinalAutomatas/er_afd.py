from argparse import ArgumentParser as AnalizadorArgumentos
from sys import stderr as salida_error, stdout as salida

from automatas import construir_afd, evaluar_cadena
from expresiones import construir_afnd, representar_caracter


def conjunto(elementos):
    return "{" + ",".join(elementos) + "}"


def mostrar_automata(automata, nombre, prefijo, alfabeto, finales):
    print(nombre)
    print("Q=" + conjunto(f"{prefijo}{estado}" for estado in range(len(automata.transiciones))))
    print("Σ=" + conjunto("ε" if simbolo is None else simbolo.texto for simbolo in alfabeto))
    print(f"Inicial={prefijo}0")
    print("F=" + conjunto(f"{prefijo}{estado}" for estado in sorted(finales)))
    if automata.alfabeto != alfabeto:
        print("Clases de entrada=" + conjunto(simbolo.texto for simbolo in automata.alfabeto))
        print("La tabla usa clases disjuntas para evitar coincidencias entre símbolos.")
    for origen, transiciones in enumerate(automata.transiciones):
        for simbolo in automata.alfabeto:
            if simbolo not in transiciones:
                continue
            destino = transiciones[simbolo]
            etiqueta = "ε" if simbolo is None else simbolo.texto
            llegada = (
                conjunto(f"{prefijo}{estado}" for estado in sorted(destino))
                if isinstance(destino, set)
                else f"{prefijo}{destino}"
            )
            print(f"{prefijo}{origen}|{etiqueta}|{llegada}")
    print()


def principal(argumentos=None):
    for flujo in (salida, salida_error):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    analizador = AnalizadorArgumentos(
        prog="er-afd",
        description="Convierte una expresión regular a AFND y AFD, y evalúa una cadena ASCII.",
        add_help=False,
    )
    analizador.add_argument("-h", "--help", action="help", help="Mostrar esta ayuda y salir.")
    analizador.add_argument("expresion", help="Expresión regular; usar comillas si contiene espacios.")
    analizador.add_argument("cadena", help="Cadena ASCII; usar comillas para espacios o la cadena vacía.")
    opciones = analizador.parse_args(argumentos)
    try:
        if not opciones.cadena.isascii():
            raise ValueError("La cadena debe contener únicamente caracteres ASCII.")
        afnd = construir_afnd(opciones.expresion)
        afd = construir_afd(afnd)
    except (ValueError, RecursionError) as error:
        mensaje = "La expresión tiene demasiados paréntesis anidados." if isinstance(error, RecursionError) else str(error)
        print(f"Error: {mensaje}", file=salida_error)
        return 2

    mostrar_automata(afnd, "AFND", "q", afnd.alfabeto, {afnd.final})
    alfabeto = [simbolo for simbolo in afnd.alfabeto if simbolo is not None]
    mostrar_automata(afd, "AFD", "Q", alfabeto, afd.finales)
    aceptada, recorrido = evaluar_cadena(afd, opciones.cadena)
    print("Recorrido")
    for origen, caracter, destino in recorrido:
        llegada = "∅" if destino is None else f"Q{destino}"
        print(f"Q{origen}|{representar_caracter(caracter)}|{llegada}")
    print("Cadena aceptada" if aceptada else "Cadena rechazada")
    return int(aceptada)


if __name__ == "__main__":
    raise SystemExit(principal())
