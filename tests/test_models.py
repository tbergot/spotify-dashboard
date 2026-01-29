"""
Tests des modèles SQLAlchemy.

Vérifie le bon fonctionnement du modèle Stream :
- Création d'enregistrements
- Gestion des champs optionnels (nullable)
- Représentation textuelle pour le débogage
"""

from datetime import UTC, datetime


class TestStreamModel:
    """Suite de tests pour le modèle Stream."""

    def test_create_stream_minimal(self, test_session, stream_model):
        """
        Vérifie la création d'un stream avec les champs minimaux requis.

        Seuls ts, username et ms_played sont obligatoires.
        Tous les autres champs doivent accepter None.
        """
        Stream = stream_model
        stream = Stream(
            ts=datetime.now(UTC),
            username="test_user",
            ms_played=180000,
        )
        test_session.add(stream)
        test_session.flush()

        # Vérifie que l'ID a été généré automatiquement
        assert stream.id is not None
        assert stream.username == "test_user"
        assert stream.ms_played == 180000

    def test_create_stream_complete(self, test_session, stream_model):
        """
        Vérifie la création d'un stream avec tous les champs remplis.

        Simule un vrai enregistrement Spotify avec toutes les métadonnées.
        """
        Stream = stream_model
        stream = Stream(
            ts=datetime.now(UTC),
            username="test_user",
            platform="iOS 17.4.1",
            conn_country="FR",
            ms_played=217773,
            track_name="Bohemian Rhapsody",
            artist_name="Queen",
            album_name="A Night at the Opera",
            spotify_track_uri="spotify:track:6l8GvAyoUZwWDgF1e4822w",
            reason_start="trackdone",
            reason_end="trackdone",
            shuffle=False,
            skipped=False,
            offline=False,
            incognito_mode=False,
            source_file="test.json",
        )
        test_session.add(stream)
        test_session.flush()

        assert stream.id is not None
        assert stream.track_name == "Bohemian Rhapsody"
        assert stream.artist_name == "Queen"
        assert stream.conn_country == "FR"

    def test_stream_repr(self, test_session, stream_model):
        """
        Vérifie la représentation textuelle d'un stream.

        La méthode __repr__ doit inclure l'artiste et le titre
        pour faciliter le débogage.
        """
        Stream = stream_model
        stream = Stream(
            ts=datetime.now(UTC),
            username="test_user",
            ms_played=0,
            track_name="My Track",
            artist_name="My Artist",
        )
        test_session.add(stream)
        test_session.flush()

        repr_str = repr(stream)
        assert "My Artist" in repr_str
        assert "My Track" in repr_str
        assert str(stream.id) in repr_str

    def test_stream_nullable_fields(self, test_session, stream_model):
        """
        Vérifie que les champs optionnels peuvent être NULL.

        Les métadonnées de piste doivent pouvoir être absentes
        (cas des streams incomplets).
        """
        Stream = stream_model
        stream = Stream(
            ts=datetime.now(UTC),
            username="test_user",
            ms_played=0,
        )
        test_session.add(stream)
        test_session.flush()

        # Tous les champs optionnels doivent être None
        assert stream.track_name is None
        assert stream.artist_name is None
        assert stream.album_name is None
        assert stream.shuffle is None
        assert stream.skipped is None

    def test_stream_default_values(self, test_session, stream_model):
        """
        Vérifie les valeurs par défaut des champs.

        incognito_mode doit être False par défaut.
        """
        Stream = stream_model
        stream = Stream(
            ts=datetime.now(UTC),
            username="test_user",
            ms_played=1000,
        )
        test_session.add(stream)
        test_session.flush()

        # Vérifie la valeur par défaut de incognito_mode
        assert stream.incognito_mode is False
