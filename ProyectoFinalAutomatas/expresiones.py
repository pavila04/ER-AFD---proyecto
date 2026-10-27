from dataclasses import dataclass


CARACTERES_ASCII = frozenset(chr(codigo) for codigo in range(128))
SECUENCIAS = {
    "N": "0123456789",
    "A": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "a": "abcdefghijklmnopqrstuvwxyz",
    "z": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
}


def representar_caracter(caracter: str) -> str:
    if not "!" <= caracter <= "~":
        return f"\\h{ord(caracter):02X}"
    return "\\" + caracter if caracter in r".|*()[]\-^,{}" else caracter


@dataclass(frozen=True)
class Simbolo:
    texto: str
    caracteres: frozenset[str]


@dataclass
class AFND:
    alfabeto: list[Simbolo | None]
    transiciones: list[dict[Simbolo | None, set[int]]]
    final: int


class Analizador:
    def __init__(self, expresion: str):
        self.expresion = expresion
        self.posicion = 0
        self.alfabeto: list[Simbolo | None] = []
        self.transiciones: list[dict[Simbolo | None, set[int]]] = []

    def actual(self) -> str:
        return self.expresion[self.posicion:self.posicion + 1]

    def error(self, mensaje: str):
        raise ValueError(f"{mensaje} (posición {self.posicion + 1}).")

    def nuevo_estado(self) -> int:
        self.transiciones.append({})
        return len(self.transiciones) - 1

    def conectar(self, origen: int, simbolo: Simbolo | None, destino: int):
        self.transiciones[origen].setdefault(simbolo, set()).add(destino)

    def fragmento(self, simbolos: list[Simbolo | None]) -> tuple[int, int]:
        inicio, final = self.nuevo_estado(), self.nuevo_estado()
        for simbolo in simbolos:
            if simbolo not in self.alfabeto:
                self.alfabeto.append(simbolo)
            self.conectar(inicio, simbolo, final)
        return inicio, final

    def literales(self, caracteres: list[str]) -> tuple[int, int]:
        return self.fragmento([
            Simbolo(representar_caracter(caracter), frozenset({caracter}))
            for caracter in dict.fromkeys(caracteres)
        ])

    def union(self) -> tuple[int, int]:
        inicio, final = self.concatenacion()
        while self.actual() == "|":
            self.posicion += 1
            otro_inicio, otro_final = self.concatenacion()
            nuevo_inicio, nuevo_final = self.nuevo_estado(), self.nuevo_estado()
            self.conectar(nuevo_inicio, None, inicio)
            self.conectar(nuevo_inicio, None, otro_inicio)
            self.conectar(final, None, nuevo_final)
            self.conectar(otro_final, None, nuevo_final)
            inicio, final = nuevo_inicio, nuevo_final
        return inicio, final

    def concatenacion(self) -> tuple[int, int]:
        if not self.actual() or self.actual() in "|)":
            self.error("Falta una expresión; usa ε para la cadena vacía")
        inicio, final = self.repeticion()
        while self.actual() and self.actual() not in "|)":
            otro_inicio, otro_final = self.repeticion()
            self.conectar(final, None, otro_inicio)
            final = otro_final
        return inicio, final

    def repeticion(self) -> tuple[int, int]:
        inicio, final = self.atomo()
        while self.actual() == "*":
            self.posicion += 1
            nuevo_inicio, nuevo_final = self.nuevo_estado(), self.nuevo_estado()
            self.conectar(nuevo_inicio, None, inicio)
            self.conectar(nuevo_inicio, None, nuevo_final)
            self.conectar(final, None, inicio)
            self.conectar(final, None, nuevo_final)
            inicio, final = nuevo_inicio, nuevo_final
        return inicio, final

    def atomo(self) -> tuple[int, int]:
        caracter = self.actual()
        if caracter in "*|)]" or not caracter:
            self.error("Se esperaba un símbolo o un grupo")
        if caracter not in CARACTERES_ASCII and caracter != "ε":
            self.error("Solo se permiten caracteres ASCII y ε")
        self.posicion += 1
        if caracter == "(":
            fragmento = self.union()
            if self.actual() != ")":
                self.error("Falta cerrar el paréntesis")
            self.posicion += 1
            return fragmento
        if caracter == "[":
            return self.conjunto()
        if caracter == "\\":
            return self.literales(self.escape())
        if caracter == ".":
            return self.fragmento([Simbolo(".", CARACTERES_ASCII)])
        if caracter == "ε":
            return self.fragmento([None])
        return self.literales([caracter])

    def escape(self) -> list[str]:
        caracter = self.actual()
        if not caracter:
            self.error("La secuencia de escape está incompleta")
        if caracter not in CARACTERES_ASCII:
            self.error("El carácter escapado debe pertenecer a ASCII")
        self.posicion += 1
        if caracter in SECUENCIAS:
            return list(SECUENCIAS[caracter])
        if caracter == "h":
            hexadecimal = self.expresion[self.posicion:self.posicion + 2]
            if len(hexadecimal) != 2 or any(
                digito not in "0123456789abcdefABCDEF" for digito in hexadecimal
            ):
                self.error("\\h requiere dos dígitos hexadecimales")
            codigo = int(hexadecimal, 16)
            if codigo > 127:
                self.error("El código hexadecimal debe pertenecer a ASCII (00-7F)")
            self.posicion += 2
            return [chr(codigo)]
        return [caracter]

    def elemento_conjunto(self) -> list[str]:
        caracter = self.actual()
        if not caracter or caracter == "]":
            self.error("Falta un carácter en el conjunto")
        if caracter not in CARACTERES_ASCII:
            self.error("Los conjuntos solo admiten caracteres ASCII")
        self.posicion += 1
        if caracter == "\\":
            return self.escape()
        return [caracter]

    def conjunto(self) -> tuple[int, int]:
        negativo = self.actual() == "^"
        if negativo:
            self.posicion += 1
        caracteres = []
        while self.actual() and self.actual() != "]":
            primero = self.elemento_conjunto()
            siguiente = self.expresion[self.posicion + 1:self.posicion + 2]
            if self.actual() == "-" and siguiente and siguiente != "]":
                self.posicion += 1
                ultimo = self.elemento_conjunto()
                if len(primero) != 1 or len(ultimo) != 1:
                    self.error("Los extremos de un rango deben ser caracteres individuales")
                if ord(primero[0]) > ord(ultimo[0]):
                    self.error("El rango debe estar en orden ascendente")
                caracteres.extend(chr(codigo) for codigo in range(
                    ord(primero[0]), ord(ultimo[0]) + 1
                ))
            else:
                caracteres.extend(primero)
        if self.actual() != "]":
            self.error("Falta cerrar el conjunto")
        if not caracteres:
            self.error("El conjunto no puede estar vacío")
        self.posicion += 1
        if negativo:
            texto = "[^" + "".join(representar_caracter(caracter) for caracter in dict.fromkeys(caracteres)) + "]"
            return self.fragmento([Simbolo(texto, CARACTERES_ASCII.difference(caracteres))])
        return self.literales(caracteres)


def construir_afnd(expresion: str) -> AFND:
    analizador = Analizador(expresion)
    inicio, final = analizador.union()
    if analizador.actual():
        analizador.error("Símbolo inesperado")
    if None not in analizador.alfabeto:
        analizador.alfabeto.append(None)

    # El inicio de Thompson puede crearse al final; se renumera para obtener q0.
    orden = [inicio] + [
        estado for estado in range(len(analizador.transiciones)) if estado != inicio
    ]
    numeros = {estado: numero for numero, estado in enumerate(orden)}
    transiciones = [
        {
            simbolo: {numeros[destino] for destino in destinos}
            for simbolo, destinos in analizador.transiciones[estado].items()
        }
        for estado in orden
    ]
    return AFND(analizador.alfabeto, transiciones, numeros[final])
