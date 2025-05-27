# CyberPlume - Votre Assistant d'Écriture Intelligent

![CyberPlume Logo](./docs/assets/logo.svg)

CyberPlume est une application d'aide à l'écriture conçue pour fonctionner localement sur votre machine. Elle vise à fournir aux écrivains une interface moderne et des outils d'assistance basés sur l'IA pour faciliter le processus de création, d'organisation et de révision de leurs œuvres.

## Table des Matières

- [Fonctionnalités Clés](#fonctionnalités-clés)
- [Technologies Utilisées](#technologies-utilisées)
- [Lancement Facile avec Docker (Recommandé)](#lancement-facile-avec-docker-recommandé)
- [Prérequis (Pour Installation Manuelle)](#prérequis-pour-installation-manuelle)
- [Installation Manuelle (Pour Développeurs)](#installation-manuelle-pour-développeurs)
- [Lancement Manuel de l'Application](#lancement-manuel-de-lapplication)
- [Dépannage (Troubleshooting)](#dépannage-troubleshooting)
- [Structure du Projet (Aperçu)](#structure-du-projet-aperçu)
- [Soutenir CyberPlume](#soutenir-cyberplume)

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
    *   **Gestion des Clés API Intégrée :** Configurez et gérez vos clés API pour les différents fournisseurs d'IA directement depuis l'interface de l'application, offrant une alternative sécurisée au stockage dans des fichiers `.env`.
*   **Outils d'Analyse Intégrés :**
    *   **Analyse de Contenu Assistée par IA :** Obtenez des suggestions pertinentes pour améliorer la qualité et le style de vos chapitres.
    *   **Analyse de Cohérence du Projet :** (Fonctionnalité en cours d'amélioration) Vérifiez la cohérence globale de votre œuvre grâce à des outils basés sur le NLP.
*   **Export et Partage Faciles (Fonctionnels !) :**
    *   **Formats Multiples :** Exportez votre travail aux formats DOCX, PDF, TXT, EPUB, ODT, et Markdown.
    *   **Niveaux d'Export :** Exportez un chapitre spécifique ou l'intégralité d'un projet.

---

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
    *   spaCy (pour l'analyse de texte NLP)
*   **Déploiement & Environnement :**
    *   Docker
    *   Docker Compose

---

## Lancement Facile avec Docker (Recommandé)

La méthode la plus simple et recommandée pour lancer CyberPlume est d'utiliser Docker et Docker Compose. Cela évite d'avoir à installer manuellement Python, Node.js et toutes les dépendances sur votre système.

**Prérequis pour Docker :**

*   **Docker Desktop** (pour Windows et macOS) ou **Docker Engine & Docker Compose** (pour Linux) installés et fonctionnels.
    *   **Vérification :** Ouvrez un terminal et tapez `docker --version` et `docker-compose --version` (ou `docker compose version` pour les versions plus récentes de Docker Desktop).
    *   **Installation :** Suivez les instructions officielles sur le [site de Docker](https://docs.docker.com/get-docker/).

**Étapes de Lancement avec Docker :**

1.  **Cloner le dépôt (si ce n'est pas déjà fait) :**
    ```bash
    git clone https://github.com/HoussenMoshine/CyberPlume.git # Remplacez par l'URL réelle si différente
    cd CyberPlume
    ```

2.  **Configuration des Variables d'Environnement :**
    CyberPlume nécessite des clés API pour accéder aux services d'IA. Vous pouvez les configurer de deux manières :
    *   **Via l'interface de l'application (Recommandé pour la simplicité) :** Une fois l'application lancée, vous pourrez entrer vos clés API directement dans la section de configuration.
    *   **Via un fichier `.env` (Optionnel, pour un pré-remplissage) :**
        1.  À la racine du projet cloné (`CyberPlume/`), créez un fichier nommé `.env`.
        2.  Vous pouvez copier le contenu de [`backend/.env.example`](backend/.env.example:0) et/ou [`frontend/.env.example`](frontend/.env.example:0) comme base, mais pour Docker, seules les clés API des services IA sont typiquement nécessaires dans ce fichier `.env` racine si vous souhaitez les pré-configurer.
            ```env
            # Exemple de contenu pour CyberPlume/.env (optionnel)
            GEMINI_API_KEY=VOTRE_CLE_API_GEMINI_ICI
            MISTRAL_API_KEY=VOTRE_CLE_API_MISTRAL_ICI
            OPENROUTER_API_KEY=VOTRE_CLE_API_OPENROUTER_ICI
            # La variable API_KEY pour la communication interne est gérée par docker-compose.yml
            ```
        *Note : La clé `API_KEY` pour la communication interne entre le frontend et le backend est déjà définie dans le fichier [`docker-compose.yml`](docker-compose.yml:0) et n'a pas besoin d'être ajoutée au fichier `.env` racine pour le lancement avec Docker, sauf si vous souhaitez la surcharger.*

3.  **Lancer les conteneurs Docker :**
    Ouvrez un terminal à la racine du projet (`CyberPlume/`) et exécutez :
    ```bash
    docker-compose up -d --build
    ```
    *   `--build` : Reconstruit les images si elles n'existent pas ou si les Dockerfiles ont changé.
    *   `-d` : Lance les conteneurs en mode détaché (en arrière-plan).

4.  **Accéder à CyberPlume :**
    Une fois les conteneurs démarrés (cela peut prendre quelques minutes la première fois), ouvrez votre navigateur web et allez à l'adresse :
    [http://localhost:5173](http://localhost:5173) (ou le port sur lequel Vite est configuré pour s'exposer via Docker, vérifiez les logs de `docker-compose up` si besoin).

5.  **Arrêter les conteneurs :**
    Pour arrêter l'application, retournez dans votre terminal à la racine du projet et exécutez :
    ```bash
    docker-compose down
    ```

---

## Prérequis (Pour Installation Manuelle)

Cette section concerne l'installation manuelle, qui est plus complexe et généralement recommandée uniquement pour les développeurs souhaitant contribuer au code. **Pour une utilisation standard, veuillez privilégier la méthode Docker ci-dessus.**

1.  **Git :** (Voir [Installation de Git](#installation-de-git) plus bas si besoin)
2.  **Python :** Version 3.11 ou plus récent. (Voir [Installation de Python](#installation-de-python))
3.  **Node.js et npm :** Node.js 18.x ou 20.x (LTS recommandé). npm est inclus. (Voir [Installation de Node.js et npm](#installation-de-nodejs-et-npm))

---

## Installation Manuelle (Pour Développeurs)

Suivez ces étapes si vous ne souhaitez pas utiliser Docker.

1.  **Cloner le dépôt :**
    <a id="installation-de-git"></a>
    Ouvrez votre terminal, naviguez vers le répertoire où vous souhaitez cloner le projet, et exécutez :
    ```bash
    git clone https://github.com/HoussenMoshine/CyberPlume.git # Remplacez par l'URL réelle si différente
    cd CyberPlume
    ```

2.  **Installation du Backend (Serveur API) :**
    <a id="installation-de-python"></a>
    *   **Naviguez vers le dossier backend :** `cd backend`
    *   **Créez et activez un environnement virtuel Python :**
        *   Linux/macOS : `python3 -m venv venv && source venv/bin/activate`
        *   Windows : `python -m venv venv && .\venv\Scripts\activate`
    *   **Installez les dépendances Python :** `pip install -r requirements.txt`
    *   **Configurez les variables d'environnement du backend :**
        1.  Copiez `cp .env.example .env` (ou `copy .env.example .env` sur Windows).
        2.  Modifiez `backend/.env` pour ajouter vos clés API (Gemini, Mistral, OpenRouter) et une `API_KEY` pour CyberPlume (chaîne aléatoire sécurisée).

3.  **Installation du Frontend (Interface Utilisateur) :**
    <a id="installation-de-nodejs-et-npm"></a>
    *   **Naviguez vers le dossier frontend :** `cd ../frontend` (depuis `backend/`) ou `cd frontend` (depuis la racine).
    *   **Installez les dépendances Node.js :** `npm install`
    *   **Configurez les variables d'environnement du frontend :**
        1.  Copiez `cp .env.example .env` (ou `copy .env.example .env` sur Windows).
        2.  Modifiez `frontend/.env` :
            *   `VITE_API_KEY` doit correspondre à la `API_KEY` définie dans `backend/.env`.
            *   `VITE_API_URL` est généralement `http://127.0.0.1:8080/api`.

---

## Lancement Manuel de l'Application

1.  **Démarrez le Backend :**
    *   Ouvrez un terminal, naviguez vers `backend/`, activez l'environnement virtuel.
    *   Lancez : `uvicorn backend.main:app --reload --port 8080`

2.  **Démarrez le Frontend :**
    *   Ouvrez un **nouveau** terminal, naviguez vers `frontend/`.
    *   Lancez : `npm run dev`
    *   L'application devrait être accessible sur l'URL affichée (généralement [http://localhost:5173](http://localhost:5173)).

---

## Dépannage (Troubleshooting)

*   **Problèmes de port :** Si le port 8080 (backend) ou 5173 (frontend) est déjà utilisé, vous devrez peut-être arrêter l'application qui l'utilise ou configurer CyberPlume pour utiliser des ports différents (plus avancé).
*   **Erreurs de proxy Vite :** Assurez-vous que `VITE_API_URL` dans `frontend/.env` pointe correctement vers votre backend et que le proxy dans [`frontend/vite.config.js`](frontend/vite.config.js:0) est bien configuré si vous avez modifié les ports par défaut.
*   **Problèmes avec l'environnement virtuel Python :** Assurez-vous qu'il est bien activé avant de lancer le backend ou d'installer des dépendances.
*   **Erreurs Docker :** Consultez les logs des conteneurs avec `docker-compose logs backend` ou `docker-compose logs frontend` pour identifier les problèmes. Assurez-vous que Docker Desktop (ou Docker Engine) est en cours d'exécution.
*   **Clés API :** Si les fonctionnalités IA ne marchent pas, vérifiez que vos clés API sont correctement configurées (soit via l'interface, soit dans les fichiers `.env` pour l'installation manuelle, soit dans le `.env` racine pour le pré-remplissage Docker).

---

## Structure du Projet (Aperçu)

```
CyberPlume/
├── backend/            # API FastAPI (Python)
│   ├── ai_services/    # Logique d'intégration des modèles IA
│   ├── routers/        # Points d'entrée de l'API (routes)
│   ├── .env.example    # Exemple de variables d'environnement backend
│   ├── config.py       # Chargement de la configuration
│   ├── crud_*.py       # Opérations CRUD sur la base de données
│   ├── database.py     # Configuration SQLAlchemy et session DB
│   ├── main.py         # Point d'entrée de l'application FastAPI
│   ├── models.py       # Modèles de données SQLAlchemy et Pydantic
│   └── requirements.txt # Dépendances Python
├── frontend/           # Application Vue.js 3 (JavaScript/Vue)
│   ├── src/
│   │   ├── assets/     # Icônes, images
│   │   ├── components/ # Composants Vue réutilisables
│   │   ├── composables/# Logique réutilisable (Composition API)
│   │   ├── plugins/    # Configuration des plugins (Vuetify)
│   │   ├── App.vue     # Composant racine de l'application
│   │   ├── main.js     # Point d'entrée de l'application Vue
│   │   └── config.js   # Configuration front-end
│   ├── .env.example    # Exemple de variables d'environnement frontend
│   ├── index.html      # Fichier HTML principal
│   ├── package.json    # Dépendances Node.js et scripts npm
│   └── vite.config.js  # Configuration de Vite (build, proxy dev)
├── instance/           # Données d'instance (ex: base de données SQLite)
│   └── cyberplume.db   # Fichier de base de données SQLite (créé au premier lancement)
├── docs/               # Documentation additionnelle
├── .gitignore          # Fichiers et dossiers ignorés par Git
├── docker-compose.yml  # Configuration pour Docker Compose
├── Dockerfile.backend  # Instructions pour construire l'image Docker du backend
├── Dockerfile.frontend-dev # Instructions pour construire l'image Docker du frontend (dev)
└── README.md           # Ce fichier
```

---

## Soutenir CyberPlume

Si vous appréciez CyberPlume ou que vous me suivez sur ma chaîne Youtube dédiée à l'IA et que vous souhaitez me soutenir, vous pouvez le faire via Patreon. Votre soutien est grandement apprécié !

[![Soutenir sur Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/houssenmoshine)