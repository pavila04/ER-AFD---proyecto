# Documentación de ER-AFD

**Estudiante:** SELVIN KLEBER GIRÓN ALVAREZ  
**Carné:** 3190-15-15973  
**Fecha:** 20 de octubre de 2026

- [Reporte técnico](reporte_tecnico.pdf): 7 páginas. Explicación del analizador, Thompson, cierre épsilon, construcción de subconjuntos y evaluación, con un ejemplo completo.
- [Casos de prueba](casos_de_prueba.pdf): 10 páginas. Resultados esperados y obtenidos, capturas y registro de la batería automatizada.
- [Manual de usuario](manual_de_usuario.pdf): 7 páginas. Requisitos, comandos de Linux y Windows, sintaxis admitida, interpretación de resultados y errores.

## Evidencias

`capturas/` contiene siete capturas de una vista de lectura en navegador de las salidas reales de Python. Algunas separan el AFND del AFD de una misma ejecución para facilitar su lectura. No representan una terminal Linux.

`evidencias/` conserva las salidas completas en archivos de texto, los códigos reales del proceso y `ejecuciones.json`, que también incluye los resultados de 152 evaluaciones dirigidas y las huellas SHA-256 de las fuentes documentadas.

La suite contiene diez métodos y verifica 42 expresiones en casos funcionales, 24 expresiones inválidas, 1,023 combinaciones de cadenas y 256 comprobaciones de complementos ASCII. Estas categorías corresponden a verificaciones diferentes y no deben sumarse como expresiones distintas.

Las ejecuciones registradas se realizaron en Windows 11 con Python 3.12.10. La validación del Makefile en Linux queda pendiente.

Para repetir la batería desde la raíz del proyecto:

```console
python pruebas.py
```

## Identificación de carátulas

Las tres carátulas incluyen el escudo proporcionado, el nombre y carné del estudiante y la fecha indicada. No se añadieron datos de docente ni de sección porque no fueron proporcionados.

## Versiones editables en Word

- [Reporte técnico editable](reporte_tecnico.docx).
- [Casos de prueba editables](casos_de_prueba.docx).
- [Manual de usuario editable](manual_de_usuario.docx).

Los archivos de Word contienen texto y tablas editables. Sus pies de página muestran únicamente el número de página, y las capturas incorporadas no incluyen la leyenda inferior de la vista de registros. Las imágenes correspondientes están en `capturas_word/`.

Los tres PDF originales se conservaron sin modificaciones.
