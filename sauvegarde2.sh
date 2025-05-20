#!/bin/bash

# === Configuration par défaut ===
DEFAULT_SOURCE_DIR="/mnt/serveur/serveur/cyberplume"
DEFAULT_SAUVEGARDE_DIR="/mnt/serveur/serveur/cyberplume-sauvegarde"
DEFAULT_EXCLUDE_FILE="" # Chemin vers un fichier d'exclusions rsync

# === Options de script ===
set -euo pipefail

# === Fonctions ===
display_help() {
    echo "Script de sauvegarde avec rsync (sans logging fichier)."
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -s, --source DIR        Répertoire source (défaut: $DEFAULT_SOURCE_DIR)"
    echo "  -d, --destination DIR   Répertoire de destination (défaut: $DEFAULT_SAUVEGARDE_DIR)"
    echo "  -e, --exclude FILE      Fichier d'exclusions rsync (défaut: aucun)"
    echo "  -n, --dry-run           Simuler la sauvegarde sans rien modifier."
    echo "  -y, --yes               Ne pas demander de confirmation (utile pour cron)."
    echo "  -h, --help              Afficher cette aide."
    echo
    echo "Exemple: $0 -s /chemin/source -d /chemin/destination"
    exit 0
}

# === Initialisation des variables ===
SOURCE_DIR="$DEFAULT_SOURCE_DIR"
SAUVEGARDE_DIR="$DEFAULT_SAUVEGARDE_DIR"
EXCLUDE_FILE="$DEFAULT_EXCLUDE_FILE"
DRY_RUN_OPT=""
ASK_CONFIRMATION=true

# === Analyse des arguments de la ligne de commande ===
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -s|--source)
        SOURCE_DIR="$2"
        shift; shift
        ;;
        -d|--destination)
        SAUVEGARDE_DIR="$2"
        shift; shift
        ;;
        -e|--exclude)
        EXCLUDE_FILE="$2"
        shift; shift
        ;;
        -n|--dry-run)
        DRY_RUN_OPT="--dry-run"
        ASK_CONFIRMATION=false
        shift
        ;;
        -y|--yes)
        ASK_CONFIRMATION=false
        shift
        ;;
        -h|--help)
        display_help
        ;;
        *)
        echo "Option inconnue: $1"
        display_help
        ;;
    esac
done

# === Interactivité ===
echo "--- Configuration de la Sauvegarde (sans log fichier) ---"

read -e -p "Répertoire source [$SOURCE_DIR]: " input_source
SOURCE_DIR="${input_source:-$SOURCE_DIR}"

read -e -p "Répertoire de sauvegarde [$SAUVEGARDE_DIR]: " input_dest
SAUVEGARDE_DIR="${input_dest:-$SAUVEGARDE_DIR}"

if [ -z "$EXCLUDE_FILE" ]; then
    read -e -p "Fichier d'exclusions rsync (laisser vide si aucun): " input_exclude
    EXCLUDE_FILE="${input_exclude:-$EXCLUDE_FILE}"
fi

echo "-------------------------------------"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Début du script de sauvegarde."

# === Vérifications ===
if [ ! -d "$SOURCE_DIR" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERREUR: Le répertoire source '$SOURCE_DIR' n'existe pas."
    exit 1
fi

if [ ! -d "$SAUVEGARDE_DIR" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Le répertoire de sauvegarde '$SAUVEGARDE_DIR' n'existe pas. Tentative de création..."
    mkdir -p "$SAUVEGARDE_DIR"
    if [ $? -eq 0 ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Répertoire de sauvegarde '$SAUVEGARDE_DIR' créé avec succès."
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ERREUR: Impossible de créer le répertoire de sauvegarde '$SAUVEGARDE_DIR'."
        exit 1
    fi
fi

if [ -n "$EXCLUDE_FILE" ] && [ ! -f "$EXCLUDE_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - AVERTISSEMENT: Le fichier d'exclusion '$EXCLUDE_FILE' n'existe pas. Il sera ignoré."
    EXCLUDE_FILE=""
fi

# === Confirmation avant exécution ===
if [ "$ASK_CONFIRMATION" = true ]; then
    echo
    echo "Récapitulatif :"
    echo "  Source:      $SOURCE_DIR"
    echo "  Destination: $SAUVEGARDE_DIR"
    [ -n "$EXCLUDE_FILE" ] && echo "  Exclusions:  $EXCLUDE_FILE"
    [ -n "$DRY_RUN_OPT" ] && echo "  Mode:        DRY-RUN (simulation)"
    echo
    echo "ATTENTION: L'option --delete est activée. Les fichiers absents de la source"
    echo "           seront supprimés de la destination '$SAUVEGARDE_DIR'."
    read -p "Voulez-vous continuer ? (o/N) " response
    if [[ ! "$response" =~ ^[oO](ui)?$ ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Sauvegarde annulée par l'utilisateur."
        exit 0
    fi
fi

# === Construction des options rsync ===
# Options : -a (archive), -v (verbeux pour voir les fichiers listés), --delete,
#           --progress (barre de progression par fichier) OU --info=progress2 (progression globale)
RSYNC_OPTS=("-av" "--delete" "--info=progress2")
# OU (souvent mieux pour la vue d'ensemble)
# RSYNC_OPTS=("-a" "--delete" "--info=progress2") # Note: -v n'est plus nécessaire avec --info=progress2

if [ -n "$DRY_RUN_OPT" ]; then
    RSYNC_OPTS+=("$DRY_RUN_OPT")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Lancement de la sauvegarde en mode DRY-RUN (simulation)."
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Lancement de la sauvegarde."
fi

if [ -n "$EXCLUDE_FILE" ]; then
    RSYNC_OPTS+=("--exclude-from=$EXCLUDE_FILE")
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Utilisation du fichier d'exclusions: $EXCLUDE_FILE"
fi

echo "Commande rsync qui sera exécutée :"
echo "rsync ${RSYNC_OPTS[*]} \"$SOURCE_DIR/\" \"$SAUVEGARDE_DIR/\""
echo # Ligne vide pour séparer

# === Exécution de rsync ===
# La sortie standard et d'erreur de rsync s'afficheront directement sur le terminal.
if rsync "${RSYNC_OPTS[@]}" \
    "$SOURCE_DIR/" \
    "$SAUVEGARDE_DIR/"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Sauvegarde terminée avec succès."
else
    rsync_exit_code=$? # Récupère le code de sortie de rsync
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERREUR: La sauvegarde a échoué (code de sortie rsync: $rsync_exit_code)."
    exit $rsync_exit_code
fi

exit 0