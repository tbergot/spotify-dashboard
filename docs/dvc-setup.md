# Configuration DVC

Ce guide explique comment initialiser DVC pour versionner les données Spotify.

## Prérequis

- DVC installé (`pip install dvc` ou via `make dev`)

## Étapes d'initialisation

### 1. Initialiser DVC

```bash
dvc init
```

Cela crée :
- `.dvc/` - configuration DVC
- `.dvcignore` - fichiers à ignorer par DVC

### 2. Ajouter les données à DVC

```bash
dvc add data/
```

Cela crée :
- `data.dvc` - fichier pointeur contenant le hash des données
- `data/.gitignore` - empêche d'autres outils de tracker les fichiers de données

## Où sont stockées les données ?

### Emplacements de stockage

| Emplacement | Contenu |
|-------------|---------|
| `data/` | Fichiers de données de travail |
| `.dvc/cache/` | Toutes les versions (stockées par hash) |
| `data.dvc` | Fichier pointeur avec le hash MD5 |

### Comment fonctionne `dvc add`

Quand vous exécutez `dvc add data/` :

1. DVC calcule le hash (MD5) des données
2. DVC copie les données dans `.dvc/cache/` (organisées par hash)
3. DVC met à jour `data.dvc` avec le nouveau hash

### Limitations sans remote configuré

Sans remote DVC configuré, les données restent uniquement sur votre machine locale :

- Les données ne sont pas sauvegardées ailleurs
- Si `.dvc/cache/` est supprimé, les versions précédentes sont perdues
- Vous ne pouvez restaurer que les versions présentes dans le cache local

Pour une sauvegarde sécurisée, configurez un remote DVC (voir section "Configuration d'un remote").

## Workflow quotidien

### Nouvel export Spotify

Quand vous recevez un nouvel export de données :

```bash
# 1. Remplacer les fichiers dans data/

# 2. Mettre à jour le tracking DVC
dvc add data/

# 3. Réimporter en base
make reimport
```

### Revenir à une version précédente

DVC conserve toutes les versions des données dans son cache (`.dvc/cache`). Pour restaurer une version précédente :

```bash
# 1. Modifier data.dvc pour pointer vers le hash de la version souhaitée
#    (récupérer le hash md5 depuis une sauvegarde ou le remote)

# 2. Restaurer les données correspondantes
dvc checkout

# 3. Réimporter en base
make reimport
```

Pour faciliter la gestion des versions, configurez un remote DVC (voir section suivante).

## Configuration d'un remote (optionnel)

Pour stocker les données sur un serveur distant (S3, GCS, SSH, etc.) :

```bash
# Exemple avec un dossier local
dvc remote add -d myremote /chemin/vers/stockage

# Exemple avec S3
dvc remote add -d myremote s3://mon-bucket/dvc-storage

# Push des données
dvc push

# Pull des données (sur une autre machine)
dvc pull
```

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `dvc status` | Voir les changements non trackés |
| `dvc diff` | Comparer avec la dernière version |
| `dvc add data/` | Tracker les changements de données |
| `dvc checkout` | Restaurer les données selon `data.dvc` |
| `dvc push` | Envoyer les données vers le remote |
| `dvc pull` | Télécharger les données depuis le remote |
