"""
Fixtures pytest pour les tests.

Fournit des fixtures réutilisables pour les tests unitaires :
- Base de données SQLite en mémoire pour isolation
- Données mock représentatives des vrais enregistrements Spotify
- Fichiers JSON temporaires pour tester l'ingestion
"""

import json
import sys
from datetime import datetime

import pytest
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# Ajout du chemin src pour les imports
sys.path.insert(0, "src")


# Modèle de test sans schéma PostgreSQL pour compatibilité SQLite
# SQLite ne supporte pas les schémas, donc on crée un modèle simplifié
class TestBase(DeclarativeBase):
    """Classe de base pour les modèles de test."""

    pass


class Stream(TestBase):
    """
    Modèle Stream pour les tests (sans schéma PostgreSQL).

    Identique au modèle de production mais sans la clause 'schema'
    pour permettre les tests avec SQLite en mémoire.
    Note: Utilise Integer au lieu de BigInteger car SQLite ne supporte
    l'autoincrement qu'avec INTEGER.
    """

    __tablename__ = "streams"

    # SQLite requiert INTEGER (pas BIGINT) pour l'autoincrement
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(100))
    conn_country: Mapped[str | None] = mapped_column(String(5))
    ip_addr_decrypted: Mapped[str | None] = mapped_column(String(50))
    user_agent_decrypted: Mapped[str | None] = mapped_column(String(500))
    ms_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    track_name: Mapped[str | None] = mapped_column(String(500))
    artist_name: Mapped[str | None] = mapped_column(String(300))
    album_name: Mapped[str | None] = mapped_column(String(500))
    spotify_track_uri: Mapped[str | None] = mapped_column(String(100))
    reason_start: Mapped[str | None] = mapped_column(String(50))
    reason_end: Mapped[str | None] = mapped_column(String(50))
    shuffle: Mapped[bool | None] = mapped_column(Boolean)
    skipped: Mapped[bool | None] = mapped_column(Boolean)
    offline: Mapped[bool | None] = mapped_column(Boolean)
    offline_timestamp: Mapped[int | None] = mapped_column(BigInteger)
    incognito_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    source_file: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Stream(id={self.id}, artist='{self.artist_name}', "
            f"track='{self.track_name}')>"
        )


# Exemple d'enregistrement Spotify représentatif pour les tests
# Contient tous les champs présents dans les vrais exports Spotify
SAMPLE_STREAM_RECORD = {
    "ts": "2024-07-19T14:33:41Z",
    "username": "test_user",
    "platform": "iOS 17.4.1 (iPhone14,5)",
    "ms_played": 217773,
    "conn_country": "FR",
    "ip_addr_decrypted": "192.168.1.1",
    "user_agent_decrypted": "Spotify/8.8.0 iOS/17.4.1",
    "master_metadata_track_name": "Test Track",
    "master_metadata_album_artist_name": "Test Artist",
    "master_metadata_album_album_name": "Test Album",
    "spotify_track_uri": "spotify:track:abc123def456",
    "reason_start": "trackdone",
    "reason_end": "trackdone",
    "shuffle": True,
    "skipped": False,
    "offline": False,
    "offline_timestamp": 1721399403,
    "incognito_mode": False,
}


@pytest.fixture(scope="session")
def test_engine():
    """
    Crée un engine SQLite en mémoire pour les tests.

    Utilise SQLite pour éviter de dépendre d'une vraie base PostgreSQL
    pendant les tests unitaires. La portée 'session' permet de réutiliser
    le même engine pour tous les tests, accélérant leur exécution.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestBase.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """
    Fournit une session de test avec rollback automatique.

    Chaque test obtient sa propre session qui est automatiquement
    annulée à la fin du test, garantissant l'isolation entre tests.
    """
    session_factory = sessionmaker(bind=test_engine)
    session = session_factory()
    yield session
    # Rollback pour nettoyer les données créées pendant le test
    session.rollback()
    session.close()


@pytest.fixture
def sample_record():
    """
    Retourne une copie de l'enregistrement de test standard.

    La copie évite les effets de bord si le test modifie le dictionnaire.
    """
    return SAMPLE_STREAM_RECORD.copy()


@pytest.fixture
def sample_json_file(tmp_path):
    """
    Crée un fichier JSON temporaire avec des données de test.

    Simule un fichier d'export Spotify réel avec 10 enregistrements
    identiques. Le nom du fichier suit la convention Spotify pour
    tester la détection du type de contenu.

    Args:
        tmp_path: Fixture pytest fournissant un répertoire temporaire

    Returns:
        Path vers le fichier JSON créé
    """
    data = [SAMPLE_STREAM_RECORD.copy() for _ in range(10)]
    filepath = tmp_path / "Streaming_History_Audio_Test.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return filepath


@pytest.fixture
def stream_model():
    """
    Fixture fournissant le modèle Stream pour les tests.

    Permet d'accéder au modèle de test depuis les tests sans
    avoir besoin d'importer directement depuis conftest.
    """
    return Stream
