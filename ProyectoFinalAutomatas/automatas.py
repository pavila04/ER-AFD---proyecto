from dataclasses import dataclass

from expresiones import AFND, CARACTERES_ASCII, Simbolo, representar_caracter


@dataclass
class AFD:
    alfabeto: list[Simbolo]
    transiciones: list[dict[Simbolo, int]]
    finales: set[int]


def representar_conjunto(caracteres: frozenset[str]) -> str:
    def agrupar(conjunto):
        codigos = sorted(map(ord, conjunto))
        partes = []
        posicion = 0
        while posicion < len(codigos):
            inicio = fin = codigos[posicion]
            posicion += 1
            while posicion < len(codigos) and codigos[posicion] == fin + 1:
                fin = codigos[posicion]
                posicion += 1
            if fin - inicio >= 2:
                partes.append(f"{representar_caracter(chr(inicio))}-{representar_caracter(chr(fin))}")
            else:
                partes.extend(representar_caracter(chr(codigo)) for codigo in range(inicio, fin + 1))
        return "".join(partes)

    if caracteres == CARACTERES_ASCII:
        return "."
    if len(caracteres) == 1:
        return representar_caracter(next(iter(caracteres)))
    positivo = f"[{agrupar(caracteres)}]"
    negativo = f"[^{agrupar(CARACTERES_ASCII - caracteres)}]"
    return min((positivo, negativo), key=len)


def separar_alfabeto(alfabeto: list[Simbolo | None]) -> list[Simbolo]:
    simbolos = [simbolo for simbolo in alfabeto if simbolo is not None]
    grupos = []
    for simbolo in simbolos:
        restantes = simbolo.caracteres
        separados = []
        for grupo in grupos:
            # Dos caracteres comparten columna si coinciden con las mismas etiquetas.
            separados.extend(parte for parte in (
                grupo & simbolo.caracteres, grupo - simbolo.caracteres
            ) if parte)
            restantes = restantes - grupo
        if restantes:
            separados.append(restantes)
        grupos = separados

    resultado = []
    for grupo in grupos:
        original = next((simbolo for simbolo in simbolos if simbolo.caracteres == grupo), None)
        resultado.append(original or Simbolo(representar_conjunto(grupo), grupo))
    return resultado


def cierre_epsilon(afnd: AFND, estados: set[int]) -> frozenset[int]:
    cierre = set(estados)
    pendientes = list(estados)
    while pendientes:
        estado = pendientes.pop()
        for destino in afnd.transiciones[estado].get(None, set()):
            if destino not in cierre:
                cierre.add(destino)
                pendientes.append(destino)
    return frozenset(cierre)


def construir_afd(afnd: AFND) -> AFD:
    alfabeto = separar_alfabeto(afnd.alfabeto)
    inicial = cierre_epsilon(afnd, {0})
    subconjuntos = [inicial]
    indices = {inicial: 0}
    transiciones = []
    finales = set()
    posicion = 0

    while posicion < len(subconjuntos):
        actuales = subconjuntos[posicion]
        if afnd.final in actuales:
            finales.add(posicion)
        fila = {}
        for simbolo in alfabeto:
            representante = min(simbolo.caracteres)
            destinos = set()
            for estado in actuales:
                for etiqueta, siguientes in afnd.transiciones[estado].items():
                    if etiqueta is not None and representante in etiqueta.caracteres:
                        destinos.update(siguientes)
            destino = cierre_epsilon(afnd, destinos)
            if destino not in indices:
                indices[destino] = len(subconjuntos)
                subconjuntos.append(destino)
            fila[simbolo] = indices[destino]
        transiciones.append(fila)
        posicion += 1

    return AFD(alfabeto, transiciones, finales)


def evaluar_cadena(afd: AFD, cadena: str) -> tuple[bool, list[tuple[int, str, int | None]]]:
    simbolos = {caracter: simbolo for simbolo in afd.alfabeto for caracter in simbolo.caracteres}
    estado = 0
    recorrido = []
    for caracter in cadena:
        simbolo = simbolos.get(caracter)
        destino = afd.transiciones[estado].get(simbolo)
        recorrido.append((estado, caracter, destino))
        if destino is None:
            return False, recorrido
        estado = destino
    return estado in afd.finales, recorrido
