#!/bin/bash

# Script pour lancer automatiquement le backend et le frontend
# dans des onglets séparés du terminal, avec activation de l'environnement virtuel

# Définir le répertoire racine du projet
PROJECT_ROOT=$(pwd)

echo "Lancement du projet depuis le répertoire: $PROJECT_ROOT"

# Vérifier l'existence de l'environnement virtuel
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Erreur: L'environnement virtuel '$PROJECT_ROOT/venv' n'existe pas!"
    echo "Veuillez créer l'environnement virtuel avant d'exécuter ce script."
    exit 1
fi

# Fonction pour lancer un service dans un nouvel onglet de terminal
launch_tab() {
    local command=$1
    local title=$2
    
    # Détection du terminal et ouverture d'un nouvel onglet
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # MacOS
        osascript -e "tell application \"Terminal\"" \
                  -e "tell application \"System Events\" to keystroke \"t\" using {command down}" \
                  -e "do script \"$command\" in front window" \
                  -e "end tell" > /dev/null
    elif [[ -n "$GNOME_TERMINAL_SERVICE" ]]; then
        # GNOME Terminal
        gnome-terminal --tab --title="$title" -- bash -c "$command; exec bash"
    elif [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
        # iTerm2
        osascript -e "tell application \"iTerm2\"" \
                  -e "tell current window to create tab with default profile" \
                  -e "tell current session of current window to write text \"$command\"" \
                  -e "end tell" > /dev/null
    elif command -v xfce4-terminal &> /dev/null; then
        # XFCE Terminal
        xfce4-terminal --tab --title="$title" -e "bash -c '$command; exec bash'" &
    elif command -v konsole &> /dev/null; then
        # KDE Konsole
        konsole --new-tab -p tabtitle="$title" -e "bash -c '$command; exec bash'" &
    else
        echo "Impossible de détecter un terminal compatible avec les onglets."
        echo "Commande à exécuter manuellement: $command"
        return 1
    fi
    
    return 0
}

# Déterminer la commande d'activation de l'environnement virtuel en fonction du système
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows avec Git Bash ou similaire
    ACTIVATE_CMD="source $PROJECT_ROOT/venv/Scripts/activate"
else
    # Linux, macOS, etc.
    ACTIVATE_CMD="source $PROJECT_ROOT/venv/bin/activate"
fi

# Lancer le backend avec activation de l'environnement virtuel
echo "Lancement du backend avec l'environnement virtuel..."
BACKEND_CMD="$ACTIVATE_CMD && cd $PROJECT_ROOT/backend && uvicorn main:app --reload --app-dir .."
launch_tab "$BACKEND_CMD" "Backend Flask"

# Attendre que le backend démarre
echo "Attente du démarrage du backend (5 secondes)..."
sleep 5

# Lancer le frontend
echo "Lancement du frontend..."
FRONTEND_CMD="cd $PROJECT_ROOT/frontend && npm run dev"
launch_tab "$FRONTEND_CMD" "Frontend NPM"

echo "Le projet a été lancé avec succès!"
echo "Pour arrêter les serveurs, fermez les onglets de terminal ou utilisez Ctrl+C dans chacun d'eux."