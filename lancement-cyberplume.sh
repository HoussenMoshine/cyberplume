#!/bin/bash

# --- Configuration ---
# Chemin vers le dossier racine de votre projet (là où se trouve 'venv')
# S'il est exécuté depuis la racine, ceci est correct. Sinon, ajustez.
PROJECT_ROOT=$(pwd)

# Chemin vers le dossier frontend (relatif à PROJECT_ROOT)
FRONTEND_DIR="frontend" # Ajustez si votre dossier frontend a un autre nom ou emplacement

# Temps d'attente (en secondes) pour que le backend démarre avant de lancer le frontend
BACKEND_STARTUP_DELAY=20 # Ajustez selon le temps que prend votre backend

# Commande pour votre terminal. Décommentez celle qui correspond à votre environnement.
# Pour GNOME (Ubuntu, Fedora, etc.)
TERMINAL_CMD="gnome-terminal"
# Pour KDE (Kubuntu, etc.)
# TERMINAL_CMD="konsole"
# Pour XFCE (Xubuntu, etc.)
# TERMINAL_CMD="xfce4-terminal"
# Pour d'autres (comme mate-terminal, lxterminal), la syntaxe peut varier.

# --- Fonctions pour la clarté ---
launch_backend() {
    echo "--- Lancement du Backend ---"
    echo "Activation de l'environnement virtuel : $PROJECT_ROOT/venv/bin/activate"
    echo "Commande backend : uvicorn backend.main:app --port 8080 --reload"
    source "$PROJECT_ROOT/venv/bin/activate"
    uvicorn backend.main:app --port 8080 --reload
    # Garde l'onglet ouvert si la commande se termine
    # exec bash
}

launch_frontend() {
    echo "--- Lancement du Frontend ---"
    echo "Navigation vers : $PROJECT_ROOT/$FRONTEND_DIR"
    echo "Commande frontend : npm run dev"
    cd "$PROJECT_ROOT/$FRONTEND_DIR"
    npm run dev
    # Garde l'onglet ouvert si la commande se termine
    # exec bash
}

# Exporter les fonctions pour qu'elles soient accessibles dans les sous-shells
export -f launch_backend
export -f launch_frontend
export PROJECT_ROOT # Pour que launch_backend/frontend le connaisse dans le nouveau terminal
export FRONTEND_DIR # Pour que launch_frontend le connaisse

# --- Script principal ---
echo "-----------------------------------------------------"
echo "Lancement automatique de l'application..."
echo "Projet racine détecté : $PROJECT_ROOT"
echo "Terminal utilisé : $TERMINAL_CMD"
echo "-----------------------------------------------------"
echo ""

# Lancer le backend dans un nouvel onglet
echo "Ouverture d'un nouvel onglet pour le Backend..."
if [ "$TERMINAL_CMD" == "gnome-terminal" ]; then
    $TERMINAL_CMD --tab --title="Backend App" --working-directory="$PROJECT_ROOT" -- bash -c "launch_backend; exec bash"
elif [ "$TERMINAL_CMD" == "konsole" ]; then
    # Konsole ouvre un nouvel onglet dans la fenêtre active si on ne spécifie pas --new-tab
    # et utilise -e pour exécuter une commande.
    # Pour garantir un nouvel onglet, il est parfois plus simple de lancer une nouvelle instance avec onglets.
    # Cette commande crée une nouvelle fenêtre Konsole avec l'onglet.
    # konsole --new-tab -p "tabtitle=Backend App" -e bash -c "cd \"$PROJECT_ROOT\"; launch_backend; exec bash"
    # Pour ajouter un onglet à la fenêtre existante (plus complexe à garantir depuis un script)
    # Il est plus fiable de lancer la commande directement dans un nouvel onglet si Konsole est déjà la fenêtre active.
    # Si ce script est lancé DEPUIS Konsole :
    # qdbus org.kde.konsole "$(qdbus org.kde.konsole | grep /Sessions/ | head -n 1)" newSession title "Backend App" bash -c "cd \"$PROJECT_ROOT\"; launch_backend; exec bash"
    # Solution plus simple mais ouvre une nouvelle fenêtre Konsole :
    $TERMINAL_CMD -p "tabtitle=Backend App" --workdir "$PROJECT_ROOT" -e bash -c "launch_backend; exec bash" &
elif [ "$TERMINAL_CMD" == "xfce4-terminal" ]; then
    $TERMINAL_CMD --tab --title="Backend App" --working-directory="$PROJECT_ROOT" --command="bash -c 'launch_backend; exec bash'"
else
    echo "Terminal non supporté pour l'ouverture d'onglets automatiques via ce script."
    echo "Veuillez lancer le backend manuellement dans un autre terminal :"
    echo "  cd \"$PROJECT_ROOT\""
    echo "  source venv/bin/activate"
    echo "  uvicorn backend.main:app --port 8080 --reload"
    # On continue quand même, au cas où l'utilisateur le fait.
fi

echo ""
echo "Attente de $BACKEND_STARTUP_DELAY secondes pour le démarrage du backend..."
sleep $BACKEND_STARTUP_DELAY
echo ""

# Lancer le frontend dans un autre nouvel onglet
echo "Ouverture d'un nouvel onglet pour le Frontend..."
if [ "$TERMINAL_CMD" == "gnome-terminal" ]; then
    $TERMINAL_CMD --tab --title="Frontend App" --working-directory="$PROJECT_ROOT/$FRONTEND_DIR" -- bash -c "launch_frontend; exec bash"
elif [ "$TERMINAL_CMD" == "konsole" ]; then
    # Voir note précédente pour Konsole
    $TERMINAL_CMD -p "tabtitle=Frontend App" --workdir "$PROJECT_ROOT/$FRONTEND_DIR" -e bash -c "launch_frontend; exec bash" &
elif [ "$TERMINAL_CMD" == "xfce4-terminal" ]; then
    $TERMINAL_CMD --tab --title="Frontend App" --working-directory="$PROJECT_ROOT/$FRONTEND_DIR" --command="bash -c 'launch_frontend; exec bash'"
else
    echo "Terminal non supporté pour l'ouverture d'onglets automatiques via ce script."
    echo "Veuillez lancer le frontend manuellement dans un autre terminal :"
    echo "  cd \"$PROJECT_ROOT/$FRONTEND_DIR\""
    echo "  npm run dev"
fi

echo ""
echo "-----------------------------------------------------"
echo "Les processus Backend et Frontend devraient être en cours de lancement dans de nouveaux onglets."
echo "Cet onglet (où le script a été lancé) peut être utilisé pour autre chose ou fermé."
echo "-----------------------------------------------------"

# Optionnel: garder cet onglet principal ouvert aussi
# exec bash