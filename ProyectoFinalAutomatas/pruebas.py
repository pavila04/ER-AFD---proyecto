from itertools import product as producto
from os import environ as entorno
from pathlib import Path as Ruta
from subprocess import run as ejecutar
from sys import executable as interprete
from unittest import TestCase as CasoPrueba, main as ejecutar_pruebas

from automatas import construir_afd, evaluar_cadena
from expresiones import CARACTERES_ASCII, construir_afnd


CASOS = [
    ("ab", ("ab",), ("", "a", "abc")),
    ("a|bc", ("a", "bc"), ("b", "ac")),
    ("(a|b)c", ("ac", "bc"), ("a", "abc")),
    ("a*", ("", "a", "aaaa"), ("b", "ab")),
    ("(a|b)*abb", ("abb", "aabb", "bababb"), ("", "ab", "abba")),
    ("ε", ("",), ("a",)),
    ("aεb", ("ab",), ("a", "aeb")),
    ("(ε|a)b", ("b", "ab"), ("", "aab")),
    ("(a*)*", ("", "aaaa"), ("b",)),
    (".", ("a", "7", " ", "\n", "\x00", "\x7f"), ("", "ab")),
    ("[abc]", ("a", "b", "c"), ("", "d", "ab")),
    ("[^abc]", ("d", "7", " "), ("a", "b", "ab")),
    ("[a-z][0-9]", ("a0", "z9"), ("A0", "a", "aa")),
    ("[a-zA-Z]*", ("", "Hola", "aZ"), ("hola1",)),
    ("[-a]", ("-", "a"), ("b",)),
    ("[a-]", ("-", "a"), ("b",)),
    (r"\*", ("*",), ("", "a")),
    (r"\p", ("p",), ("q",)),
    (r"\\", ("\\",), ("", "/")),
    (r"\.", (".",), ("a",)),
    (r"\|", ("|",), ("a",)),
    (r"\(a\)", ("(a)",), ("a",)),
    (r"\N\N*", ("0", "12345"), ("", "1a")),
    (r"\h20", (" ",), ("", "20")),
    (r"\h41", ("A",), ("a",)),
    (r"\h00", ("\x00",), ("0",)),
    (r"\h7F", ("\x7f",), ("F",)),
    (r"\A\A*", ("A", "HOLA"), ("", "Hola")),
    (r"\a\a*", ("a", "hola"), ("", "Hola")),
    (r"\z\z*", ("A", "Hola"), ("", "Hola1")),
    (r"[\Nabc]", ("0", "9", "b"), ("d", "ab")),
    (r"[^\N]", ("a", " "), ("0", "9")),
    (r"[\h41-\h43]", ("A", "B", "C"), ("D",)),
    (r"[\]\-]", ("]", "-"), ("a",)),
    ("hola mundo", ("hola mundo",), ("holamundo",)),
    (r"hola\ mundo", ("hola mundo",), ("holamundo",)),
    (".b|ac", ("ab", "ac", "zb"), ("aa", "bc")),
    ("a.|ab", ("ab", "ac"), ("a", "ba")),
    ("[^a]b|ac", ("bb", "ac"), ("ab", "bc")),
    ("[^ab]|[^bc]", ("a", "c", "z"), ("b", "")),
    (r"[^\h00-\h7F]", (), ("", "a", "\x00")),
    (r"[^\h00-\h7F]*", ("",), ("a",)),
]

INVALIDAS = [
    "", "(", "(a", "a)", "()", "|a", "a|", "a||b", "*a",
    "[", "[abc", "[]", "[^]", "[z-a]", "]", "\\", r"\h",
    r"\h2", r"\hGG", r"\h80", r"[\N-a]", r"[a-\N]", "ñ", "[ñ]",
]


class PruebasAutomatas(CasoPrueba):
    def test_cadenas(self):
        for expresion, aceptadas, rechazadas in CASOS:
            afd = construir_afd(construir_afnd(expresion))
            for esperado, cadenas in ((True, aceptadas), (False, rechazadas)):
                for cadena in cadenas:
                    with self.subTest(expresion=expresion, cadena=cadena):
                        self.assertEqual(evaluar_cadena(afd, cadena)[0], esperado)

    def test_expresiones_invalidas(self):
        for expresion in INVALIDAS:
            with self.subTest(expresion=expresion):
                with self.assertRaises(ValueError) as error:
                    construir_afnd(expresion)
                self.assertIn("posición", str(error.exception))

    def test_orden_alfabeto(self):
        for expresion, esperado in (
            ("bεa.b", ["b", None, "a", "."]),
            ("ba.b", ["b", "a", ".", None]),
        ):
            afnd = construir_afnd(expresion)
            self.assertEqual([None if simbolo is None else simbolo.texto
                              for simbolo in afnd.alfabeto], esperado)

    def test_clases_sin_solapamientos(self):
        for expresion in (".b|ac", "[^ab]|[^bc]", r"[a-z]|\z", r".\N*"):
            afnd = construir_afnd(expresion)
            afd = construir_afd(afnd)
            vistos = set()
            for simbolo in afd.alfabeto:
                self.assertTrue(vistos.isdisjoint(simbolo.caracteres))
                vistos.update(simbolo.caracteres)
            esperado = set().union(*(simbolo.caracteres for simbolo in afnd.alfabeto
                                    if simbolo is not None))
            self.assertEqual(vistos, esperado)

    def test_complementos_ascii(self):
        for expresion, excluidos in (("[^abc]", set("abc")), (r"[^\N]", set("0123456789"))):
            afd = construir_afd(construir_afnd(expresion))
            for caracter in CARACTERES_ASCII:
                with self.subTest(expresion=expresion, caracter=caracter):
                    self.assertEqual(evaluar_cadena(afd, caracter)[0], caracter not in excluidos)

    def test_combinaciones(self):
        for expresion, condicion in (
            ("(a|b)*abb", lambda cadena: all(caracter in "ab" for caracter in cadena) and cadena.endswith("abb")),
            (".b|ac", lambda cadena: len(cadena) == 2 and (cadena[1] == "b" or cadena == "ac")),
            ("[^a]b|ac", lambda cadena: len(cadena) == 2 and (
                (cadena[0] != "a" and cadena[1] == "b") or cadena == "ac")),
        ):
            afd = construir_afd(construir_afnd(expresion))
            for longitud in range(5):
                for caracteres in producto("abc0", repeat=longitud):
                    cadena = "".join(caracteres)
                    with self.subTest(expresion=expresion, cadena=cadena):
                        self.assertEqual(evaluar_cadena(afd, cadena)[0], condicion(cadena))

    def ejecutar_consola(self, argumentos, archivo="er_afd.py", codificacion="utf-8"):
        carpeta = Ruta(__file__).resolve().parent
        return ejecutar(
            [interprete, str(carpeta / archivo), *argumentos],
            capture_output=True, text=True, encoding="utf-8", timeout=10,
            env={**entorno, "PYTHONIOENCODING": codificacion},
        )

    def test_consola(self):
        for archivo in ("er_afd.py", "er-afd"):
            for cadena, codigo, mensaje in (("aabb", 1, "Cadena aceptada"), ("abba", 0, "Cadena rechazada")):
                with self.subTest(archivo=archivo, cadena=cadena):
                    resultado = self.ejecutar_consola(["(a|b)*abb", cadena], archivo)
                    self.assertEqual(resultado.returncode, codigo)
                    self.assertEqual(resultado.stderr, "")
                    self.assertIn("Inicial=q0", resultado.stdout)
                    self.assertIn("Inicial=Q0", resultado.stdout)
                    self.assertIn("Recorrido\nQ0|a|Q", resultado.stdout)
                    self.assertTrue(resultado.stdout.rstrip().endswith(mensaje))

    def test_consola_errores(self):
        for argumentos in (["[z-a]", "a"], ["a", "ñ"], ["a"], [], ["(" * 300 + "a" + ")" * 300, "a"]):
            with self.subTest(argumentos=argumentos):
                resultado = self.ejecutar_consola(argumentos)
                self.assertEqual(resultado.returncode, 2)
                self.assertTrue(resultado.stderr)
                self.assertNotIn("Traceback", resultado.stderr)

    def test_consola_codificacion_windows(self):
        resultado = self.ejecutar_consola(["a", "a"], codificacion="cp1252")
        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(resultado.stderr, "")
        self.assertIn("Σ={a,ε}", resultado.stdout)
        self.assertIn("Cadena aceptada", resultado.stdout)

    def test_consola_cadena_vacia_y_guion(self):
        for argumentos in (["a*", ""], ["--", "-a", "-a"]):
            with self.subTest(argumentos=argumentos):
                resultado = self.ejecutar_consola(argumentos)
                self.assertEqual(resultado.returncode, 1)
                self.assertEqual(resultado.stderr, "")
                self.assertIn("Cadena aceptada", resultado.stdout)


if __name__ == "__main__":
    ejecutar_pruebas(verbosity=2)
