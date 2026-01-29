# Spotify Dashboard

Analyse de mon historique d'écoute Spotify.

## Prérequis

- Python 3.11+
- PostgreSQL 16 (via Homebrew)
- Make

## Installation

### 1. Cloner le projet et créer l'environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
make dev
```

### 3. Configurer l'environnement

```bash
cp .env.example .env
```

Modifier `.env` si nécessaire (les valeurs par défaut fonctionnent).

### 4. Lancer le setup complet

```bash
make all
```

Cette commande :
- Démarre PostgreSQL
- Crée la base de données et les tables
- Ingère les données JSON (~121k enregistrements)

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `make help` | Affiche l'aide |
| `make pg-start` | Démarre PostgreSQL |
| `make pg-stop` | Arrête PostgreSQL |
| `make db-init` | Crée le schéma et les tables |
| `make ingest` | Ingère les données JSON |
| `make reimport` | Vide la table et réimporte les données |
| `make all` | Setup complet |
| `make test` | Lance les tests pytest |
| `make lint` | Vérifie le code avec Ruff |
| `make format` | Formate le code |

## Structure du projet

```
spotify-dashboard/
├── data/                   # Fichiers JSON Spotify (versionnés via DVC)
├── docs/
│   └── dvc-setup.md        # Guide d'initialisation Git + DVC
├── notebooks/
│   └── spotify_analysis.ipynb  # Analyse EDA avec Plotly
├── src/spotify_dashboard/
│   ├── config.py           # Configuration .env
│   ├── database.py         # Connexion SQLAlchemy
│   └── models.py           # Modèle Stream
├── tools/
│   ├── init_db.py          # Initialisation de la base
│   └── ingest.py           # Script d'ingestion
├── tests/                  # Tests pytest
├── Makefile                # Commandes d'automatisation
└── pyproject.toml          # Configuration Python et Ruff
```

## Base de données

- **Schéma** : `streaming_history`
- **Table** : `streams` (~121 000 enregistrements)

### Champs principaux

| Champ | Description |
|-------|-------------|
| `ts` | Horodatage de l'écoute |
| `track_name` | Nom de la piste |
| `artist_name` | Nom de l'artiste |
| `album_name` | Nom de l'album |
| `ms_played` | Durée d'écoute (ms) |
| `platform` | Plateforme utilisée |
| `conn_country` | Pays de connexion |
| `shuffle` | Mode aléatoire activé |
| `skipped` | Piste passée |

## Analyses disponibles

Le notebook inclut :

1. **Vue d'ensemble** - Statistiques générales
2. **Analyse temporelle** - Évolution par année, mois, jour, heure
3. **Top artistes** - Classement par streams et temps d'écoute
4. **Top pistes et albums** - Avec analyse des skips
5. **Plateformes** - Répartition iOS/macOS/Web/Android
6. **Géographie** - Répartition par pays
7. **Comportement** - Shuffle, offline, skip rate
8. **Tendances** - Découverte de nouveaux artistes, fidélité

## Développement

### Lancer les tests

```bash
make test
```

### Vérifier le style du code

```bash
make lint
```

### Formater le code

```bash
make format
```

## Gestion des données avec DVC

Les fichiers JSON Spotify sont versionnés avec [DVC](https://dvc.org/) (Data Version Control).

Voir [docs/dvc-setup.md](docs/dvc-setup.md) pour le guide complet d'initialisation.

### Réimporter après un nouvel export

```bash
# Remplacer les fichiers dans data/
dvc add data/
make reimport
```

## Technologies

- **Python 3.11+**
- **PostgreSQL 16**
- **SQLAlchemy 2.x** - ORM
- **Pandas** - Manipulation de données
- **Plotly** - Visualisations interactives
- **Pydantic** - Validation et configuration
- **DVC** - Versioning des données
- **Ruff** - Linting et formatage
- **pytest** - Tests
