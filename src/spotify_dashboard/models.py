"""
Modèles SQLAlchemy pour la base de données Spotify.

Définit la structure de la table streams qui contient l'historique d'écoute
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""

    pass


class Stream(Base):
    """Modèle représentant un stream audio Spotify.

    Chaque enregistrement correspond à une écoute unique avec toutes les
    métadonnées associées.

    Le schéma 'streaming_history' est utilisé pour isoler les données
    de l'historique d'écoute des autres tables éventuelles.
    """

    __tablename__ = "streams"
    __table_args__ = (
        # Index pour les requêtes fréquentes
        Index("idx_streams_ts", "ts"),
        Index("idx_streams_artist", "artist_name"),
        Index("idx_streams_track", "track_name"),
        Index("idx_streams_platform", "platform"),
        Index("idx_streams_country", "conn_country"),
        # Index composite pour les analyses temporelles par artiste
        Index("idx_streams_artist_ts", "artist_name", "ts"),
        {"schema": "streaming_history"},
    )

    # Clé primaire auto-incrémentée
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Horodatage de l'écoute et identifiant utilisateur
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)

    # Contexte technique de lecture
    platform: Mapped[str | None] = mapped_column(String(100))
    conn_country: Mapped[str | None] = mapped_column(String(5))
    ip_addr_decrypted: Mapped[str | None] = mapped_column(String(50))
    user_agent_decrypted: Mapped[str | None] = mapped_column(String(500))

    # Durée d'écoute en millisecondes
    ms_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Métadonnées de la piste
    track_name: Mapped[str | None] = mapped_column(String(500))
    artist_name: Mapped[str | None] = mapped_column(String(300))
    album_name: Mapped[str | None] = mapped_column(String(500))
    spotify_track_uri: Mapped[str | None] = mapped_column(String(100))

    # Contexte de lecture
    reason_start: Mapped[str | None] = mapped_column(String(50))
    reason_end: Mapped[str | None] = mapped_column(String(50))
    shuffle: Mapped[bool | None] = mapped_column(Boolean)
    skipped: Mapped[bool | None] = mapped_column(Boolean)
    offline: Mapped[bool | None] = mapped_column(Boolean)
    offline_timestamp: Mapped[int | None] = mapped_column(BigInteger)
    incognito_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    # Fichier source pour traçabilité
    source_file: Mapped[str | None] = mapped_column(String(100))

    # Timestamp de création de l'enregistrement en base
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        """Représentation textuelle du stream pour le debug."""
        return (
            f"<Stream(id={self.id}, artist='{self.artist_name}', "
            f"track='{self.track_name}')>"
        )
