#!/usr/bin/env python3
"""
Script d'initialisation de la base de données.

Ce script crée le schéma 'streaming_history' et les tables nécessaires
sans insérer de données.

Usage:
    python -m tools.init_db
"""

import logging
import sys

from sqlalchemy import text

# Ajout du chemin src pour les imports
sys.path.insert(0, "src")

from spotify_dashboard.database import engine
from spotify_dashboard.models import Base

# Configuration du logging avec format lisible
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_database() -> None:
    """
    Initialise la base de données en créant le schéma et les tables.

    Étapes:
        1. Création du schéma 'streaming_history' si inexistant
        2. Création de toutes les tables définies dans les modèles SQLAlchemy
    """
    logger.info("Démarrage de l'initialisation de la base de données...")

    # Création du schéma PostgreSQL pour isoler les données
    logger.info("Création du schéma 'streaming_history'...")
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS streaming_history"))
        conn.commit()

    # Suppression et recréation des tables pour appliquer les changements de schéma
    logger.info("Suppression des tables existantes...")
    Base.metadata.drop_all(bind=engine)

    logger.info("Création des tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Base de données initialisée avec succès!")


if __name__ == "__main__":
    init_database()
