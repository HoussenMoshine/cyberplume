# CyberPlume - Votre Assistant d'Écriture Intelligent

![CyberPlume Logo](./docs/assets/logo.svg)

CyberPlume est une application d'aide à l'écriture conçue pour fonctionner localement sur votre machine. Elle vise à fournir aux écrivains une interface moderne et des outils d'assistance basés sur l'IA pour faciliter le processus de création, d'organisation et de révision de leurs œuvres.

## Fonctionnalités Clés

CyberPlume offre une suite d'outils intégrés pour accompagner les écrivains à chaque étape de leur processus créatif :

*   **Interface d'Écriture Intuitive :**
    *   **Éditeur de Texte Riche :** Basé sur TipTap, offrant une expérience d'édition WYSIWYG fluide et complète.
    *   **Sauvegarde Fiable :** Mécanismes de sauvegarde automatique et manuelle pour ne jamais perdre votre travail.
*   **Assistance IA Contextuelle :**
    *   **Génération de Texte :** Des fonctionnalités comme "Continuer", "Suggérer un dialogue" pour surmonter le syndrome de la page blanche.
    *   **Manipulation de Texte :** Outils pour "Reformuler", "Raccourcir", ou "Étendre" des passages existants.
    *   **Aide Spécifique :** Assistance pour la génération et le développement de personnages et de scènes.
*   **Gestion de Projet d'Écriture Avancée :**
    *   **Organisation Structurée :** Gérez vos écrits de manière hiérarchique avec des Projets, Chapitres, et Scènes (création, lecture, mise à jour, suppression, et ordonnancement facile).
    *   **Métadonnées :** Attribuez des informations détaillées (métadonnées) à vos chapitres et scènes pour une meilleure organisation.
    *   **Gestion des Personnages :** Un module dédié pour créer et gérer des fiches personnages détaillées (descriptions, traits, historique, etc.) et les lier à vos projets.
*   **Intégration IA Configurable et Flexible :**
    *   **Support Multi-Fournisseurs :** Connectez-vous à différents modèles d'IA via Gemini, Mistral, OpenRouter, et d'autres à venir, grâce à une architecture modulaire.
    *   **Sélection Dynamique :** Choisissez facilement le fournisseur et le modèle IA que vous souhaitez utiliser via l'interface.
    *   **Personnalisation :** Ajustez les paramètres de l'IA (comme la température, la longueur maximale) et guidez le style de génération.
*   **Export et Partage Faciles :**
    *   **Formats Multiples :** Exportez votre travail aux formats DOCX, PDF, TXT, EPUB, ODT, et Markdown.
    *   **Niveaux d'Export :** Exportez un chapitre spécifique ou l'intégralité d'un projet.

## Technologies Utilisées

*   **Backend :**
    *   Python 3.11+
    *   FastAPI (Framework Web)
    *   SQLAlchemy (ORM)
    *   SQLite (Base de données)
    *   Pydantic (Validation de données)
*   **Frontend :**
    *   Vue.js 3 (Composition API)
    *   Vuetify 3 (Bibliothèque UI Material Design)
    *   TipTap 2 (Éditeur de texte riche)
    *   Vite (Outil de build)
    *   Axios (Client HTTP)
*   **IA :**
    *   Bibliothèques clientes spécifiques : `google-generativeai`, `mistralai`, `openai` (pour OpenRouter).

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

1.  **Git :**
    *   **Vérification :** Ouvrez un terminal et tapez `git --version`.
    *   **Installation :**
        *   **Linux (Debian/Ubuntu) :** `sudo apt update && sudo apt install git`
        *   **Linux (Fedora) :** `sudo dnf install git`
        *   **macOS :** Git est souvent préinstallé. Sinon, il sera proposé à l'installation avec les outils de développement Xcode Command Line Tools. Vous pouvez aussi l'installer via [Homebrew](https://brew.sh/) : `brew install git`.
        *   **Windows :** Téléchargez et installez [Git for Windows](https://git-scm.com/download/win).

2.  **Python :**
    *   **Version :** 3.11 ou plus récent.
    *   **Vérification :** Ouvrez un terminal et tapez `python --version` ou `python3 --version`.
    *   **Installation :**
        *   **Linux :** Généralement préinstallé. Utilisez le gestionnaire de paquets de votre distribution si nécessaire (ex: `sudo apt install python3.11 python3.11-venv`).
        *   **macOS :** Peut être installé via le [site officiel Python](https://www.python.org/downloads/macos/) ou Homebrew (`brew install python`).
        *   **Windows :** Téléchargez l'installeur depuis le [site officiel Python](https://www.python.org/downloads/windows/). **Assurez-vous de cocher "Add Python to PATH"** lors de l'installation.

3.  **Node.js et npm :**
    *   **Node.js Version :** 18.x ou 20.x (LTS recommandé). npm est inclus avec Node.js.
    *   **Vérification :** Ouvrez un terminal et tapez `node -v` puis `npm -v`.
    *   **Installation :**
        *   **Linux & macOS :** La méthode recommandée est d'utiliser [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm).
            1.  Installez nvm : `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash` (vérifiez la dernière version sur le dépôt nvm).
            2.  Sourcez votre profil shell (ex: `source ~/.bashrc`, `source ~/.zshrc`) ou ouvrez un nouveau terminal.
            3.  Installez Node.js LTS : `nvm install --lts`
        *   **Windows :** Téléchargez l'installeur LTS depuis le [site officiel Node.js](https://nodejs.org/).

## Installation

1.  **Cloner le dépôt :**
    Ouvrez votre terminal, naviguez vers le répertoire où vous souhaitez cloner le projet, et exécutez :
    ```bash
    git clone https://github.com/VOTRE_UTILISATEUR/NOM_DU_DEPOT.git
    cd NOM_DU_DEPOT
    ```
    *(Remplacez `VOTRE_UTILISATEUR/NOM_DU_DEPOT` par l'URL réelle du dépôt une fois créé).*

2.  **Installation du Backend (Serveur API) :**

    *   **Naviguez vers le dossier backend :**
        ```bash
        cd backend
        ```

    *   **Créez un environnement virtuel Python :**
        *   **Linux/macOS :**
            ```bash
            python3 -m venv venv
            ```
        *   **Windows (CMD) :**
            ```bash
            python -m venv venv
            ```
        *   **Windows (PowerShell) :**
            ```powershell
            python -m venv venv
            ```
        *(Cela crée un dossier `venv` dans le répertoire `backend`)*

    *   **Activez l'environnement virtuel :**
        *   **Linux/macOS (bash/zsh) :**
            ```bash
            source venv/bin/activate
            ```
        *   **Windows (CMD) :**
            ```batch
            venv\Scripts\activate.bat
            ```
        *   **Windows (PowerShell) :**
            ```powershell
            .\venv\Scripts\Activate.ps1
            ```
            *(Si vous obtenez une erreur concernant l'exécution des scripts sur PowerShell, vous devrez peut-être exécuter `Set-ExecutionPolicy Unrestricted -Scope Process` puis réessayer. N'oubliez pas de remettre la politique à son état précédent après, si nécessaire, par exemple `Set-ExecutionPolicy Restricted -Scope Process`)*
        *(Votre invite de terminal devrait maintenant indiquer que l'environnement `(venv)` est actif)*

    *   **Installez les dépendances Python :**
        ```bash
        pip install -r requirements.txt
        ```

    *   **Configurez les variables d'environnement du backend :**
        1.  Copiez le fichier d'exemple :
            *   **Linux/macOS :** `cp .env.example .env`
            *   **Windows (CMD/PowerShell) :** `copy .env.example .env`
        2.  Ouvrez le fichier `backend/.env` nouvellement créé avec un éditeur de texte.
        3.  Remplissez les clés API nécessaires (pour Gemini, Mistral, OpenRouter) et la clé `API_KEY` pour CyberPlume.
            ```env
            GEMINI_API_KEY=VOTRE_CLE_API_GEMINI_ICI
            MISTRAL_API_KEY=VOTRE_CLE_API_MISTRAL_ICI
            OPENROUTER_API_KEY=VOTRE_CLE_API_OPENROUTER_ICI
            API_KEY=VOTRE_CLE_API_CYBERPLUME_ICI
            ```
            *(La `API_KEY` est utilisée pour sécuriser la communication entre le frontend et le backend. Vous pouvez générer une chaîne aléatoire sécurisée pour cela).*

3.  **Installation du Frontend (Interface Utilisateur) :**

    *   **Naviguez vers le dossier frontend (depuis la racine du projet) :**
        ```bash
        cd ../frontend
        ```
        *(Si vous étiez dans `backend/`, sinon `cd frontend` depuis la racine)*

    *   **Installez les dépendances Node.js :**
        ```bash
        npm install
        ```

    *   **Configurez les variables d'environnement du frontend :**
        1.  Copiez le fichier d'exemple :
            *   **Linux/macOS :** `cp .env.example .env`
            *   **Windows (CMD/PowerShell) :** `copy .env.example .env`
        2.  Ouvrez le fichier `frontend/.env` nouvellement créé.
        3.  Assurez-vous que les variables sont correctement configurées :
            ```env
            VITE_API_KEY=LA_MEME_CLE_QUE_API_KEY_DANS_BACKEND/.ENV
            VITE_API_URL=http://127.0.0.1:8080/api
            ```
            *   `VITE_API_KEY` doit correspondre à la `API_KEY` que vous avez définie dans `backend/.env`.
            *   `VITE_API_URL` est généralement `http://127.0.0.1:8080/api` pour le développement local, car le serveur de développement Vite (sur un autre port, ex: 5173) proxyfiera les requêtes `/api` vers le backend FastAPI qui tourne sur le port 8080.

## Lancement de l'Application

Pour lancer CyberPlume, vous devez démarrer le serveur backend PUIS le serveur de développement frontend.

1.  **Démarrez le Backend :**
    *   Ouvrez un terminal.
    *   Naviguez vers le dossier `backend/`.
    *   Activez l'environnement virtuel (si ce n'est pas déjà fait) :
        *   Linux/macOS : `source venv/bin/activate`
        *   Windows CMD : `venv\Scripts\activate.bat`
        *   Windows PowerShell : `.\venv\Scripts\Activate.ps1`
    *   Lancez le serveur FastAPI :
        ```bash
        uvicorn backend.main:app --reload --port 8080
        ```
        *(Le backend devrait maintenant tourner sur `http://127.0.0.1:8080`)*

2.  **Démarrez le Frontend :**
    *   Ouvrez un **nouveau** terminal (laissez le backend tourner dans le premier).
    *   Naviguez vers le dossier `frontend/`.
    *   Lancez le serveur de développement Vite :
        ```bash
        npm run dev
        ```
        *(Vite vous indiquera l'URL sur laquelle le frontend est accessible, généralement `http://localhost:5173` ou un port similaire).*

3.  **Accédez à CyberPlume :**
    *   Ouvrez votre navigateur web et allez à l'URL fournie par Vite pour le frontend (ex: `http://localhost:5173`).

## Dépannage (Troubleshooting)

Voici quelques problèmes courants que vous pourriez rencontrer et leurs solutions :

*   **Erreur "Port déjà utilisé" (Address already in use) :**
    *   **Cause :** Un autre service utilise déjà le port sur lequel le backend (8080) ou le frontend (ex: 5173) essaie de démarrer.
    *   **Solution Backend (Port 8080) :**
        *   Vous pouvez changer le port dans la commande de lancement : `uvicorn backend.main:app --reload --port AUTRE_PORT` (ex: `--port 8081`).
        *   Si vous changez le port du backend, n'oubliez pas de mettre à jour `VITE_API_URL` dans `frontend/.env` en conséquence (ex: `http://127.0.0.1:8081/api`).
    *   **Solution Frontend (Port Vite) :**
        *   Vite essaiera automatiquement un autre port s'il est occupé. Si vous voulez forcer un port spécifique, vous pouvez modifier le script `dev` dans `frontend/package.json` : `"dev": "vite --port NOUVEAU_PORT"`.
    *   **Identifier le processus utilisant un port :**
        *   **Linux/macOS :** `sudo lsof -i :PORT` (ex: `sudo lsof -i :8080`). Puis `kill -9 PID_DU_PROCESSUS`.
        *   **Windows (CMD) :** `netstat -ano | findstr :PORT`. Trouvez le PID et utilisez `taskkill /PID VOTRE_PID /F`.
        *   **Windows (PowerShell) :** `Get-NetTCPConnection -LocalPort PORT | Select-Object -ExpandProperty OwningProcess | Get-Process -Id {$_.Id} | Stop-Process -Force`.

*   **Erreurs liées aux clés API (ex: 401 Unauthorized, 403 Forbidden, erreurs spécifiques du fournisseur IA) :**
    *   **Cause :** Les clés API dans `backend/.env` sont incorrectes, manquantes, ou n'ont pas les permissions nécessaires auprès du fournisseur IA. La `API_KEY` (pour la communication frontend-backend) ne correspond pas entre `backend/.env` et `frontend/.env`.
    *   **Solution :**
        1.  Vérifiez attentivement que les clés API dans `backend/.env` sont correctes et valides.
        2.  Assurez-vous que la variable `API_KEY` dans `backend/.env` est identique à `VITE_API_KEY` dans `frontend/.env`.
        3.  Consultez la documentation du fournisseur IA concerné si l'erreur persiste.

*   **Oubli d'activation de l'environnement virtuel Python (`venv`) :**
    *   **Symptômes :** Erreurs `ModuleNotFoundError` pour des paquets listés dans `requirements.txt` lorsque vous essayez de lancer le backend.
    *   **Solution :** Assurez-vous d'activer l'environnement virtuel (`source venv/bin/activate` ou équivalent Windows) avant de lancer `uvicorn`.

*   **Problèmes de proxy ou CORS :**
    *   **Symptômes :** Le frontend ne parvient pas à communiquer avec le backend, erreurs CORS dans la console du navigateur.
    *   **Solution :**
        1.  Vérifiez que `VITE_API_URL` dans `frontend/.env` est correcte (généralement `http://127.0.0.1:8080/api`).
        2.  Assurez-vous que le backend FastAPI a la configuration CORS appropriée (dans `backend/main.py`, cela devrait déjà être géré pour autoriser les origines locales).
        3.  Vérifiez la configuration du proxy dans `frontend/vite.config.js`.

*   **Le modèle de langue spaCy n'est pas trouvé :**
    *   **Symptômes :** Erreur lors de l'utilisation d'une fonctionnalité d'analyse de texte, mentionnant un modèle manquant (ex: `fr_core_news_md`).
    *   **Solution :** Après avoir installé les dépendances de `backend/requirements.txt`, vous devez télécharger le modèle spaCy manuellement. Activez votre environnement virtuel backend et exécutez :
        ```bash
        python -m spacy download fr_core_news_md
        ```

## Structure du Projet (Aperçu)

```
cyberplume/
├── backend/                # API Backend (FastAPI, Python)
│   ├── .env.example        # Exemple de fichier d'environnement pour le backend
│   ├── .gitignore          # Fichiers ignorés par Git pour le backend
│   ├── ai_services/        # Modules pour l'intégration des services IA
│   ├── routers/            # Logique des routes API (endpoints)
│   ├── tests/              # Tests pour le backend
│   ├── config.py           # Configuration (chargement des variables d'env)
│   ├── database.py         # Configuration de la base de données (SQLAlchemy)
│   ├── main.py             # Point d'entrée de l'application FastAPI
│   ├── models.py           # Modèles de données (SQLAlchemy & Pydantic)
│   └── requirements.txt    # Dépendances Python
│
├── docs/                   # Documentation du projet
│   └── assets/
│       └── logo.svg        # Logo de l'application
│   └── plan-preparation-github.md # Plan de préparation GitHub
│
├── frontend/               # Application Frontend (Vue.js, Vuetify)
│   ├── .env.example        # Exemple de fichier d'environnement pour le frontend
│   ├── .gitignore          # Fichiers ignorés par Git pour le frontend
│   ├── public/             # Assets statiques publics
│   ├── src/                # Code source du frontend
│   │   ├── assets/         # Images, polices, etc. (autres que le logo principal)
│   │   ├── components/     # Composants Vue réutilisables
│   │   ├── composables/    # Logique réutilisable (Composition API)
│   │   ├── plugins/        # Configuration des plugins (ex: Vuetify)
│   │   ├── App.vue         # Composant racine de l'application Vue
│   │   ├── main.js         # Point d'entrée de l'application Vue
│   │   └── config.js       # Configuration spécifique au frontend
│   ├── index.html          # Point d'entrée HTML
│   ├── package.json        # Dépendances et scripts npm
│   └── vite.config.js      # Configuration de Vite (outil de build)
│
├── instance/               # Fichiers d'instance (ex: base de données locale)
│   └── cyberplume.db       # Base de données SQLite (ignorée par .gitignore du backend)
│
├── .gitignore              # Fichiers ignorés par Git à la racine du projet
└── README.md               # Ce fichier
```

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez contribuer, veuillez d'abord ouvrir une "issue" pour discuter des changements que vous aimeriez apporter.