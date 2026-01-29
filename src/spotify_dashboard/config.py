"""
Configuration de l'application.

Ce module charge les variables d'environnement et fournit les paramètres
de configuration pour la connexion à la base de données PostgreSQL.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration de l'application chargée depuis les variables d'environnement.

    Les variables peuvent être définies dans un fichier .env à la racine du projet.
    Utilise pydantic-settings pour la validation et le chargement automatique.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paramètres de connexion PostgreSQL
    # Ces valeurs peuvent être surchargées via les variables d'environnement
    postgres_user: str = "spotify"
    postgres_password: str = "spotify_secret"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "spotify_db"

    # URL de connexion complète (peut être définie directement)
    database_url: str = ""

    # Répertoire contenant les fichiers JSON de données
    data_dir: Path = Path("./data")

    def model_post_init(self, __context) -> None:
        """
        Construit l'URL de base de données si elle n'est pas fournie directement.

        Cette méthode est appelée automatiquement après l'initialisation du modèle
        pour générer l'URL de connexion à partir des paramètres individuels.
        """
        if not self.database_url:
            self.database_url = (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )


# Instance globale des paramètres, importable depuis les autres modules
settings = Settings()
