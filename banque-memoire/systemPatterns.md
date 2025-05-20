# Patrons Système - CyberPlume (Mise à jour : 17/05/2025 - 06:20)

## Architecture Générale

CyberPlume adopte une architecture client-serveur locale :

*   **Backend (Serveur API) :** Une API RESTful développée avec **FastAPI**. Elle gère la logique métier, les interactions avec la base de données, l'intégration des services IA externes et la génération des exports. Les endpoints sont typiquement structurés sans préfixe `/api` dans leur définition (ex: `/projects`, `/models/{provider}`).
*   **Frontend (Client Lourd Local) :** Une Single Page Application (SPA) développée avec **Vue.js 3**. Elle fournit l'interface utilisateur et interagit avec l'API backend via des requêtes HTTP (`axios`).
    *   En développement, les appels API du frontend (ex: vers `/api/models/{provider}`) sont dirigés vers le serveur de développement Vite, qui utilise un **proxy** ([`frontend/vite.config.js`](frontend/vite.config.js:1)) pour les transmettre au backend FastAPI (ex: sur `http://127.0.0.1:8080`). Ce proxy gère également la réécriture de chemin (ex: supprimer le préfixe `/api` initial) pour correspondre aux attentes du backend.
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
    
    subgraph Dev Environment
        VA
    end

    subgraph Serveur Local
        B
        C
        E
    end

    subgraph Services Tiers
        D
    end
```
*(Diagramme mis à jour pour refléter le proxy Vite en développement et la suppression de PydanticAI - 16/05)*

## Structure du Projet (Conceptuelle)

La structure de code vise à séparer clairement les responsabilités :

```
cyberplume/
├── backend/            # API FastAPI
│   ├── main.py         # Point d'entrée, routers principaux, config CORS, middleware
│   ├── database.py     # Configuration et session SQLAlchemy
│   ├── models.py       # Modèles SQLAlchemy (tables DB) & Pydantic (validation API)
│   ├── crud.py         # Fonctions d'accès et de manipulation de la base de données
│   ├── routers/        # Modules contenant les routes API par fonctionnalité.
│   │                   # Chaque routeur définit son propre préfixe (ex: /projects, /chapters).
│   │                   # L'accès global via le frontend se fait souvent via /api/... qui est ensuite réécrit par le proxy Vite.
│   │   └── ...
│   └── ai_services/    # Logique d'intégration IA (Adapters directs)
│
├── frontend/           # Application Vue.js 3
│   ├── src/
│   │   ├── main.js       # Point d'entrée Vue
│   │   ├── App.vue       # Composant racine
│   │   ├── components/   # Composants UI
│   │   ├── composables/  # Logique réutilisable
│   │   ├── plugins/      # Configuration des plugins Vue
│   │   │   └── vuetify.js
│   │   └── utils/        # Utilitaires
│   ├── vite.config.js  # Configuration du build et du proxy de dev Vite
│   └── ...
└── instance/
    └── cyberplume.db
```
*(Structure mise à jour pour refléter la suppression des agents IA - 16/05)*

## Patrons de Conception Clés

*   **API RESTful (Backend) :** Standard.
*   **Modèle-Vue-ViewModel (MVVM) / Composition API (Frontend) :** Standard.
*   **Repository Pattern (Backend - via `crud.py`) :** Standard.
*   **Factory Pattern (Backend - `ai_services/factory.py`) :** Pour les adaptateurs IA directs.
*   **Adapter Pattern (Backend - `ai_services/*_adapter.py`) :** Pour les adaptateurs IA directs.
*   **Injection de Dépendances (Backend - via FastAPI) :** Standard.

## Relations et Flux Critiques

*   **Chargement/Sauvegarde Chapitre :** Frontend (`ProjectManager` -> `useChapterContent` -> `EditorComponent`) demande `/chapters/{id}` -> Backend (`crud.get_chapter`) -> DB.
*   **Action IA (Directe - Éditeur) :** Frontend (`EditorComponent`/`ActionPanel` -> `useAIActions`) demande `/generate/text` -> Backend (routeur IA -> `factory.get_ai_service` -> `adapter.generate_text`) -> Service IA Externe.
*   **Analyse de Contenu :** Frontend (`ProjectManager` -> `useAnalysis`) demande `/chapters/{id}/analyze-content` -> Backend (routeur d'analyse -> `nlp_service`) -> DB.

*Ce document est basé sur l'architecture et la structure décrites dans `docs/plan-cyber-plume.md` et inférées de la structure de code existante et des sessions de développement récentes.*