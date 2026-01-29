"""
Module de connexion à la base de données PostgreSQL.

Fournit l'engine SQLAlchemy et un context manager pour gérer les sessions
de manière sécurisée avec commit/rollback automatique.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from spotify_dashboard.config import settings

# Création de l'engine avec paramètres de pool de connexions
# pool_pre_ping vérifie que la connexion est valide avant utilisation
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# Factory de sessions pour créer des sessions liées à l'engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager pour obtenir une session de base de données.

    Gère automatiquement le commit en cas de succès, le rollback en cas
    d'erreur, et la fermeture de la session dans tous les cas.

    Exemple d'utilisation:
        with get_session() as session:
            streams = session.query(Stream).all()
            # Le commit est automatique à la sortie du bloc
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        # En cas d'erreur, on annule toutes les modifications
        session.rollback()
        raise
    finally:
        # La session est toujours fermée, même en cas d'erreur
        session.close()
