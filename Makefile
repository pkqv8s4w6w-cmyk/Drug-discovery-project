# VERIDIAN. Stage order is enforced here, not merely documented (ADR-001).
.PHONY: help setup test lint typecheck smoke gate dev full clean
.DEFAULT_GOAL := help

VENV    := .venv
PY      := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
VERIDIAN:= $(VENV)/bin/veridian

help:
	@echo "VERIDIAN"
	@echo "  make setup   venv, deps, docking binaries"
	@echo "  make test    test suite (one xfail is intentional)"
	@echo "  make lint    ruff"
	@echo "  make smoke   ~60 ligands, one receptor, ~7.5 min"
	@echo "  make gate    the pre-registered go/no-go, ~24 h"
	@echo "  make dev     ~2,000 ligands, ~9.6 h"
	@echo "  make full    emits a job spec; NOT runnable here (~87 days)"

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

setup: $(VENV)
	$(PIP) install -r requirements/dev.txt
	$(PIP) install -r requirements/dock.txt
	$(PIP) install -e .
	@echo ""
	@echo "Docking binaries are not on pip. Install via apt:"
	@echo "    sudo apt-get install -y autodock-vina openbabel"
	@echo "or conda-forge (also provides smina):"
	@echo "    micromamba install -c conda-forge vina smina openbabel"
	@echo "gnina is unavailable in this environment -- see ADR-005."
	@$(VENV)/bin/veridian --version

test: ; $(VENV)/bin/pytest
lint: ; $(VENV)/bin/ruff check src tests
typecheck: ; $(VENV)/bin/mypy src

smoke: ; $(VERIDIAN) smoke

# ADR-001: no library is enumerated until the gate passes.
runs/gate/PASS:
	$(VERIDIAN) gate

gate: ; $(VERIDIAN) gate

dev: runs/gate/PASS
	$(VERIDIAN) dev

full: runs/gate/PASS
	@echo "Full tier is ~87 days of brute-force docking on 4 cores (ADR-010)."
	@echo "Emitting a job spec for external execution instead."
	$(VERIDIAN) full --dry-run

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
