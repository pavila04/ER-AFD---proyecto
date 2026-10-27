PITON ?= python3
EXPRESION ?= (a|b)*abb
CADENA ?= aabb

export EXPRESION CADENA

.PHONY: config build run clean

config:
	@$(PITON) -c "import sys as sistema; raise SystemExit(0 if sistema.version_info >= (3, 10) else 'Se requiere Python 3.10 o superior.')"

build: config
	@chmod +x er-afd

run: build
	@$(PITON) er-afd -- "$$EXPRESION" "$$CADENA"; codigo=$$?; if [ $$codigo -gt 1 ]; then exit $$codigo; fi

clean:
	@rm -rf __pycache__
