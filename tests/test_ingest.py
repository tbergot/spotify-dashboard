"""
Tests du script d'ingestion.

Vérifie les fonctions utilitaires du module d'ingestion :
- Détection du type de contenu (audio/video)
- Découverte des fichiers JSON
- Chargement des enregistrements
- Transformation des données
"""

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from tools.ingest import (
    discover_json_files,
    load_json_records,
    transform_record,
)


class TestDiscoverJsonFiles:
    """Tests pour la fonction discover_json_files."""

    def test_find_audio_files(self, tmp_path):
        """Vérifie la découverte des fichiers audio JSON."""
        # Création de fichiers de test
        (tmp_path / "Streaming_History_Audio_Test.json").write_text("[]")
        (tmp_path / "other_file.txt").write_text("test")

        files = discover_json_files(tmp_path)

        assert len(files) == 1
        assert files[0].name == "Streaming_History_Audio_Test.json"

    def test_find_multiple_files(self, tmp_path):
        """Vérifie la découverte de plusieurs fichiers audio."""
        (tmp_path / "Streaming_History_Audio_2020.json").write_text("[]")
        (tmp_path / "Streaming_History_Audio_2021.json").write_text("[]")
        (tmp_path / "Streaming_History_Audio_2022.json").write_text("[]")

        files = discover_json_files(tmp_path)

        assert len(files) == 3
        # Vérifie que les fichiers sont triés
        assert files[0].name == "Streaming_History_Audio_2020.json"

    def test_empty_directory(self, tmp_path):
        """Vérifie le comportement avec un répertoire vide."""
        files = discover_json_files(tmp_path)
        assert files == []

    def test_no_matching_files(self, tmp_path):
        """Vérifie le comportement quand aucun fichier ne correspond au pattern."""
        (tmp_path / "random_file.json").write_text("[]")
        (tmp_path / "other_data.json").write_text("[]")

        files = discover_json_files(tmp_path)
        assert files == []


class TestLoadJsonRecords:
    """Tests pour la fonction load_json_records."""

    def test_load_records(self, sample_json_file):
        """Vérifie le chargement correct des enregistrements JSON."""
        records = list(load_json_records(sample_json_file))

        assert len(records) == 10
        assert all(r["username"] == "test_user" for r in records)
        assert all(r["platform"] == "iOS 17.4.1 (iPhone14,5)" for r in records)

    def test_load_records_generator(self, sample_json_file):
        """Vérifie que load_json_records retourne un générateur."""
        result = load_json_records(sample_json_file)
        # Un générateur a une méthode __next__
        assert hasattr(result, "__next__")


class TestTransformRecord:
    """Tests pour la fonction transform_record."""

    def test_transform_record(self, sample_record):
        """Vérifie la transformation d'un enregistrement audio."""
        result = transform_record(sample_record, "test.json")

        # Vérifie le mapping des champs de métadonnées
        assert result["track_name"] == "Test Track"
        assert result["artist_name"] == "Test Artist"
        assert result["album_name"] == "Test Album"

        # Vérifie les métadonnées d'ingestion
        assert result["source_file"] == "test.json"

        # Vérifie que les anciens noms de champs ne sont pas présents
        assert "master_metadata_track_name" not in result
        assert "master_metadata_album_artist_name" not in result

    def test_transform_preserves_all_fields(self, sample_record):
        """Vérifie que tous les champs attendus sont présents après transformation."""
        result = transform_record(sample_record, "test.json")

        expected_fields = {
            "ts",
            "username",
            "platform",
            "conn_country",
            "ip_addr_decrypted",
            "user_agent_decrypted",
            "ms_played",
            "track_name",
            "artist_name",
            "album_name",
            "spotify_track_uri",
            "reason_start",
            "reason_end",
            "shuffle",
            "skipped",
            "offline",
            "offline_timestamp",
            "incognito_mode",
            "source_file",
        }

        assert set(result.keys()) == expected_fields

    def test_transform_handles_missing_fields(self):
        """Vérifie la gestion des champs manquants dans l'enregistrement source."""
        minimal_record = {
            "ts": "2024-01-01T00:00:00Z",
            "username": "user",
        }

        result = transform_record(minimal_record, "test.json")

        # Les champs manquants doivent être None ou avoir une valeur par défaut
        assert result["ms_played"] == 0
        assert result["track_name"] is None
        assert result["incognito_mode"] is False
