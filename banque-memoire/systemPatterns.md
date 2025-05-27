# Patrons Système - CyberPlume (Mise à jour : 27/05/2025 - 07:21)

## Architecture Générale

CyberPlume adopte une architecture client-serveur locale, déployable via Docker Compose ou manuellement pour le développement.

### 1. Architecture de Lancement (Docker Compose - Recommandé)

```mermaid
graph LR
    User[Utilisateur] -- HTTP --> Browser[Navigateur Web];
    Browser -- HTTP (localhost:5173) --> DockerNet[Réseau Docker];

    subgraph DockerNet
        direction LR
        F_Container[Frontend Container (Vite/Node.js)];
        B_Container[Backend Container (FastAPI/Uvicorn)];
        DB_Volume[Volume DB (SQLite)];

        F_Container -- HTTP (sur réseau interne Docker) --> B_Container;
        B_Container -- SQLAlchemy --> DB_Volume;
        B_Container -- Adapters IA --> ExtIA[Services IA Externes];
        B_Container -- Bibliothèques Python --> ExtExport[Génération Export];
    end

    User --> F_Container; # Accès via port exposé
```
*   **Frontend Container :** Sert l'application Vue.js (build de production ou serveur de dev Vite selon le Dockerfile).
*   **Backend Container :** Exécute l'API FastAPI avec Uvicorn.
*   **Communication Inter-Conteneurs :** Gérée par le réseau Docker défini dans `docker-compose.yml`.
*   **Persistance des Données :** Le volume Docker assure la persistance de la base de données SQLite.

### 2. Architecture en Développement (Manuel)

*   **Backend (Serveur API) :** Une API RESTful développée avec **FastAPI**. Elle gère la logique métier, les interactions avec la base de données, l'intégration des services IA externes et la génération des exports. Les endpoints sont typiquement structurés sans préfixe `/api` dans leur définition (ex: `/projects`, `/models/{provider}`).
*   **Frontend (Client Lourd Local) :** Une Single Page Application (SPA) développée avec **Vue.js 3**. Elle fournit l'interface utilisateur et interagit avec l'API backend via des requêtes HTTP (`axios`).
    *   En développement manuel, les appels API du frontend (ex: vers `/api/models/{provider}`) sont dirigés vers le serveur de développement Vite, qui utilise un **proxy** ([`frontend/vite.config.js`](frontend/vite.config.js:1)) pour les transmettre au backend FastAPI (ex: sur `http://127.0.0.1:8080`). Ce proxy gère également la réécriture de chemin.
*   **Base de Données :** Une base de données **SQLite** locale (`instance/cyberplume.db`), gérée par le backend via **SQLAlchemy** (ORM).

```mermaid
graph LR
    A[Frontend (Vue.js 3 + Vuetify 3)] -- HTTP (axios) --> VA[Vite Dev Server (avec Proxy)];
    VA -- HTTP --> B(Backend API (FastAPI sur port 8080));
    B -- SQLAlchemy --> C(Base de Données (SQLite));
    B -- Adapters IA --> D(Services IA Externes);
    B -- Bibliothèques Python --> E(Génération Export);

    subgraph Client (Navigateur)
        A
    end
    
    subgraph Dev Environment (Manuel)
        VA
    end

    subgraph Serveur Local (Manuel)
        B
        C
        E
    end

    subgraph Services Tiers
        D
    end
```

## Structure du Projet (Conceptuelle)

La structure de code vise à séparer clairement les responsabilités :

```
cyberplume/
├── backend/            # API FastAPI
│   ├── main.py         # Point d'entrée, routers principaux, config CORS, middleware
│   ├── database.py     # Configuration et session SQLAlchemy
│   ├── models.py       # Modèles SQLAlchemy (tables DB) & Pydantic (validation API)
│   ├── crud_*.py       # Fonctions d'accès et de manipulation de la base de données
│   ├── routers/        # Modules contenant les routes API par fonctionnalité.
│   └── ai_services/    # Logique d'intégration IA (Adapters directs)
│
├── frontend/           # Application Vue.js 3
│   ├── src/
│   │   ├── main.js       # Point d'entrée Vue
│   │   ├── App.vue       # Composant racine
│   │   ├── components/   # Composants UI (dont ApiKeysManager.vue)
│   │   ├── composables/  # Logique réutilisable
│   │   └── ...
│   ├── vite.config.js  # Configuration du build et du proxy de dev Vite
│   └── ...
│
├── instance/
│   └── cyberplume.db   # Base de données SQLite (persistée via volume Docker)
│
├── .env                # Variables d'environnement pour Docker Compose (optionnel, pour clés API IA)
├── docker-compose.yml  # Configuration pour le lancement multi-conteneurs
├── Dockerfile.backend  # Instructions de build pour l'image Docker backend
├── Dockerfile.frontend-dev # Instructions de build pour l'image Docker frontend
└── README.md
```

## Patrons de Conception Clés

*   **API RESTful (Backend) :** Standard.
*   **Modèle-Vue-ViewModel (MVVM) / Composition API (Frontend) :** Standard.
*   **Repository Pattern (Backend - via `crud_*.py`) :** Standard.
*   **Factory Pattern (Backend - `ai_services/factory.py`) :** Pour les adaptateurs IA.
*   **Adapter Pattern (Backend - `ai_services/*_adapter.py`) :** Pour les adaptateurs IA.
*   **Injection de Dépendances (Backend - via FastAPI) :** Standard.

## Relations et Flux Critiques

*   **Chargement/Sauvegarde Chapitre :** Frontend (`ProjectManager` -> `useChapterContent` -> `EditorComponent`) demande `/chapters/{id}` -> Backend (`crud_chapters.get_chapter_content`) -> DB.
*   **Action IA (Directe - Éditeur) :** Frontend (`EditorComponent`/`ActionPanel` -> `useAIActions`) demande `/generate/text` (ou similaire) -> Backend (routeur IA -> `factory.get_ai_service` -> `adapter.generate_text`) -> Service IA Externe.
*   **Analyse de Contenu (Chapitre) :** Frontend (`ProjectManager` -> `useAnalysis`) demande `/chapters/{id}/analyze-content` -> Backend (routeur d'analyse -> service IA via factory/adapter) -> Service IA Externe.
*   **Analyse de Cohérence (Projet) :** Frontend demande `/projects/{id}/analyze-coherence` -> Backend (routeur d'analyse -> utilise `spaCy` et logique interne).
*   **Export Projet/Chapitre :** Frontend (ex: `ProjectToolbar`) demande `/export/project/{project_id}?format=docx` -> Backend (routeur d'export -> service d'export spécifique au format) -> Fichier téléchargé.
*   **Gestion des Clés API (Interface) :** Frontend ([`frontend/src/components/ApiKeysManager.vue`](frontend/src/components/ApiKeysManager.vue:0)) interagit avec les endpoints `/api-keys-config/*` -> Backend (`routers/api_keys_config.py`) -> DB (pour sauvegarde/lecture des clés chiffrées).

*Ce document est basé sur l'architecture et la structure décrites dans `docs/plan-cyber-plume.md` et inférées de la structure de code existante et des sessions de développement récentes.*