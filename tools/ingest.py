#!/usr/bin/env python3
"""
Script d'ingestion des données Spotify dans PostgreSQL.

Lit les fichiers JSON de l'historique d'écoute audio exporté depuis Spotify
et les insère dans la base de données PostgreSQL.

Usage:
    python -m tools.ingest --data-dir ./data
    python -m tools.ingest --data-dir ./data --dry-run  # Simulation
"""

import argparse
import json
import logging
import sys
from collections.abc import Generator
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, "src")

from sqlalchemy import text
from sqlalchemy.orm import Session

from spotify_dashboard.database import get_session
from spotify_dashboard.models import Stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande.

    Returns:
        Namespace contenant les arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Ingestion des données Spotify dans PostgreSQL"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./data"),
        help="Répertoire contenant les fichiers JSON (défaut: ./data)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Taille des lots d'insertion (défaut: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simule l'ingestion sans écrire en base",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Vide la table avant l'import (pour réimport complet)",
    )
    return parser.parse_args()


def discover_json_files(data_dir: Path) -> list[Path]:
    """Découvre les fichiers JSON d'historique audio Spotify dans le répertoire.

    Recherche les fichiers correspondant au pattern Streaming_History_Audio_*.json
    qui est le format d'export standard de Spotify pour les pistes audio.

    Args:
        data_dir: Chemin vers le répertoire contenant les fichiers

    Returns:
        Liste triée des chemins vers les fichiers JSON trouvés
    """
    json_files = list(data_dir.glob("Streaming_History_Audio_*.json"))
    if not json_files:
        logger.warning("Aucun fichier JSON audio trouvé dans %s", data_dir)
    return sorted(json_files)


def load_json_records(filepath: Path) -> Generator[dict, None, None]:
    """Charge les enregistrements JSON d'un fichier.

    Utilise un générateur pour permettre le traitement en streaming,
    bien que le fichier soit chargé en mémoire (limitation du format JSON).

    Args:
        filepath: Chemin vers le fichier JSON

    Yields:
        Dictionnaire représentant chaque enregistrement d'écoute
    """
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
        yield from data


def clear_table(session: Session) -> None:
    """Vide la table streams avant réimport.

    Utilise TRUNCATE pour une suppression rapide avec reset de la séquence
    d'identifiants. Plus performant que DELETE pour vider une table entière.

    Args:
        session: Session SQLAlchemy active
    """
    logger.info("Vidage de la table streams...")
    session.execute(text("TRUNCATE TABLE streaming_history.streams RESTART IDENTITY"))
    session.commit()
    logger.info("Table vidée avec succès")


def transform_record(record: dict, source_file: str) -> dict:
    """Transforme un enregistrement JSON brut en dictionnaire pour insertion.

    Effectue le mapping entre les noms de champs Spotify et les colonnes
    de notre table. Les champs avec préfixe 'master_metadata_' sont
    renommés pour plus de clarté.

    Args:
        record: Enregistrement JSON brut depuis le fichier Spotify
        source_file: Nom du fichier source pour traçabilité

    Returns:
        Dictionnaire prêt pour créer une instance Stream
    """
    return {
        "ts": record["ts"],
        "username": record["username"],
        "platform": record.get("platform"),
        "conn_country": record.get("conn_country"),
        "ip_addr_decrypted": record.get("ip_addr_decrypted"),
        "user_agent_decrypted": record.get("user_agent_decrypted"),
        "ms_played": record.get("ms_played", 0),
        # Mapping des champs de métadonnées piste
        "track_name": record.get("master_metadata_track_name"),
        "artist_name": record.get("master_metadata_album_artist_name"),
        "album_name": record.get("master_metadata_album_album_name"),
        "spotify_track_uri": record.get("spotify_track_uri"),
        # Contexte de lecture
        "reason_start": record.get("reason_start"),
        "reason_end": record.get("reason_end"),
        "shuffle": record.get("shuffle"),
        "skipped": record.get("skipped"),
        "offline": record.get("offline"),
        "offline_timestamp": record.get("offline_timestamp"),
        "incognito_mode": record.get("incognito_mode", False),
        # Métadonnées d'ingestion
        "source_file": source_file,
    }


def insert_batch(session: Session, records: list[dict]) -> int:
    """Insère un lot de streams dans la base de données.

    Utilise bulk_save_objects pour optimiser l'insertion de masse.
    Le commit est effectué après chaque lot pour éviter les transactions
    trop longues.

    Args:
        session: Session SQLAlchemy active
        records: Liste de dictionnaires à insérer

    Returns:
        Nombre de streams insérés
    """
    streams = [Stream(**record) for record in records]
    session.bulk_save_objects(streams)
    session.commit()
    return len(streams)


def ingest_file(
    session: Session,
    filepath: Path,
    batch_size: int,
    dry_run: bool = False,
) -> int:
    """
    Ingère un fichier JSON complet dans la base de données.

    Args:
        session: Session SQLAlchemy active
        filepath: Chemin vers le fichier JSON à ingérer
        batch_size: Nombre d'enregistrements par lot d'insertion
        dry_run: Si True, simule l'ingestion sans écrire en base

    Returns:
        Nombre total d'enregistrements traités
    """
    source_file = filepath.name

    logger.info("Traitement de %s...", filepath.name)

    batch: list[dict] = []
    total_inserted = 0

    # Chargement des enregistrements avec barre de progression
    records = list(load_json_records(filepath))

    for record in tqdm(records, desc=filepath.name, unit="records"):
        transformed = transform_record(record, source_file)
        batch.append(transformed)

        # Insertion du batch quand il est plein
        if len(batch) >= batch_size:
            if not dry_run:
                total_inserted += insert_batch(session, batch)
            else:
                total_inserted += len(batch)
            batch = []

    # Insertion du dernier lot partiel (s'il reste des enregistrements)
    if batch:
        if not dry_run:
            total_inserted += insert_batch(session, batch)
        else:
            total_inserted += len(batch)

    status = "simulés" if dry_run else "insérés"
    logger.info("  -> %d enregistrements %s", total_inserted, status)
    return total_inserted


def main() -> None:
    """
    Point d'entrée principal du script d'ingestion.

    Orchestre la découverte des fichiers, l'ouverture de la session DB,
    et l'ingestion de chaque fichier dans l'ordre.
    """
    args = parse_args()

    logger.info("Ingestion des données Spotify")
    logger.info("Répertoire de données: %s", args.data_dir)
    logger.info("Taille des lots: %d", args.batch_size)

    if args.dry_run:
        logger.warning("Mode simulation activé - aucune donnée ne sera écrite")

    # Découverte des fichiers JSON audio à traiter
    json_files = discover_json_files(args.data_dir)
    logger.info("Fichiers trouvés: %d", len(json_files))

    if not json_files:
        logger.error("Aucun fichier à traiter, arrêt du script")
        return

    # Ingestion de chaque fichier avec une session partagée
    total_records = 0

    with get_session() as session:
        # Vider la table si demandé (pour réimport complet)
        if args.clear and not args.dry_run:
            clear_table(session)

        for filepath in json_files:
            count = ingest_file(
                session=session,
                filepath=filepath,
                batch_size=args.batch_size,
                dry_run=args.dry_run,
            )
            total_records += count

    logger.info("Ingestion terminée: %d enregistrements", total_records)


if __name__ == "__main__":
    main()
