.PHONY: help install dev pg-start pg-stop pg-create-user pg-drop-db pg-create-db db-init ingest reimport test lint format black black-check clean notebook all

PYTHON := python3
DATA_DIR := ./data

help:  ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installe les dépendances de base
	$(PYTHON) -m pip install -e .

dev:  ## Installe les dépendances de développement
	$(PYTHON) -m pip install -e ".[dev,notebook]"

pg-start:  ## Démarre PostgreSQL
	brew services start postgresql@16
	@echo "En attente de PostgreSQL..."
	@sleep 3

pg-stop:  ## Arrête PostgreSQL
	brew services stop postgresql@16

pg-create-user:  ## Crée l'utilisateur PostgreSQL spotify
	/usr/local/opt/postgresql@16/bin/psql postgres -c "CREATE USER spotify WITH PASSWORD 'spotify_secret';" 2>/dev/null || echo "Utilisateur spotify existe déjà"

pg-drop-db:  ## Supprime la base de données spotify_db
	/usr/local/opt/postgresql@16/bin/dropdb spotify_db 2>/dev/null || echo "Base spotify_db n'existe pas"

pg-create-db: pg-create-user  ## Crée la base de données spotify_db
	/usr/local/opt/postgresql@16/bin/createdb -O spotify spotify_db 2>/dev/null || echo "Base spotify_db existe déjà"

db-init:  ## Initialise le schéma de la base de données
	$(PYTHON) -m tools.init_db

ingest:  ## Ingère les données dans PostgreSQL
	$(PYTHON) -m tools.ingest --data-dir $(DATA_DIR)

reimport:  ## Réimporte les données (vide la table puis ingère)
	$(PYTHON) -m tools.ingest --data-dir $(DATA_DIR) --clear

test:  ## Lance les tests pytest
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:  ## Vérifie le code avec Ruff
	$(PYTHON) -m ruff check src/ tools/ tests/

format:  ## Formate le code avec Ruff
	$(PYTHON) -m ruff format src/ tools/ tests/
	$(PYTHON) -m ruff check --fix src/ tools/ tests/

black:  ## Formate le code avec Black (inclut notebooks)
	$(PYTHON) -m black src/ tools/ tests/ notebooks/

black-check:  ## Vérifie le formatage Black sans modifier
	$(PYTHON) -m black --check src/ tools/ tests/ notebooks/

clean:  ## Nettoie les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov/

all: pg-start pg-create-db db-init ingest  ## Setup complet (PostgreSQL + ingestion)
	@echo "Setup terminé avec succès!"
