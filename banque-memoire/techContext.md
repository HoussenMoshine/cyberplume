# Contexte Technique - CyberPlume (Mise à jour : 05/06/2025 - 09:50)

## Technologies Principales

### Backend
*   **Langage :** Python (3.11+)
*   **Framework Web :** FastAPI
*   **Base de Données :** SQLite (via fichier local `instance/cyberplume.db`)
*   **ORM :** SQLAlchemy
*   **Validation des Données (API) :** Pydantic
*   **Environnement Virtuel (pour dev manuel) :** `venv`
*   **Configuration du Logging :** Gérée pour Uvicorn via un fichier externe ([`log_config.yaml`](log_config.yaml:0)) en développement manuel.

### Frontend
*   **Langage :** JavaScript (ES6+)
*   **Framework :** Vue.js 3 (utilisant la Composition API)
*   **Bibliothèque UI :** Vuetify 3 (pour les composants Material Design)
*   **Éditeur de Texte Riche :** TipTap 2
*   **Client HTTP :** `axios` (pour les appels API vers le backend)
*   **Gestionnaire de Paquets (pour dev manuel) :** npm
*   **Outil de Build :** Vite.
    *   Utilise un serveur proxy en développement ([`frontend/vite.config.js`](frontend/vite.config.js:1)) pour rediriger les appels `/api/*` vers le backend FastAPI (ex: port 8080) avec réécriture de chemin pour supprimer le préfixe `/api`.

### Déploiement et Environnement de Lancement
*   **Conteneurisation :** Docker
*   **Orchestration (locale) :** Docker Compose

## Bibliothèques et Services Clés

### Backend
*   **Intégration IA :**
    *   Bibliothèques spécifiques aux fournisseurs (ex: `google-generativeai`, `mistralai`, `openai` pour OpenRouter).
*   **Export (Fonctionnels) :**
    *   `python-docx` (pour DOCX)
    *   `xhtml2pdf` ou `reportlab` (pour PDF)
    *   `ebooklib` (pour EPUB)
    *   `html2text` (pour TXT/Markdown)
*   **Traitement du Langage Naturel (NLP) :**
    *   `spaCy` (utilisé pour l'analyse de cohérence/contenu)
    *   `beautifulsoup4` (utilisé pour l'extraction de texte brut avant analyse)
*   **Serveur ASGI :** Uvicorn (utilisé pour lancer FastAPI en développement manuel et dans le conteneur Docker).

### Frontend
*   **Composants Vuetify :** Utilisation extensive. Configuration du thème dans [`frontend/src/plugins/vuetify.js`](frontend/src/plugins/vuetify.js:0).
*   **TipTap Extensions :** Extensions de base.
*   **Icônes (Bibliothèque) :** `@tabler/icons-vue` pour les icônes génériques.
*   **Icônes (Personnalisées) :** Fichiers SVG stockés dans [`frontend/src/assets/`](frontend/src/assets/) et intégrés.
*   **Configuration Globale :** [`frontend/src/config.js`](frontend/src/config.js:1) charge la configuration de l'application.

## Configuration et Lancement

### Méthode Recommandée : Docker
*   **Lancement :**
    *   `docker-compose up -d --build` à la racine du projet.
    *   Accès via [http://localhost:5173](http://localhost:5173) (port frontend exposé).
*   **Variables d'Environnement (Clés API IA) :**
    *   **Option 1 (Recommandée) :** Configurer directement via l'interface de l'application après le lancement.
    *   **Option 2 (Pré-remplissage) :** Créer un fichier `.env` à la racine du projet (ex: `CyberPlume/.env`) et y ajouter les clés (ex: `GEMINI_API_KEY=...`). Ce fichier est lu par `docker-compose.yml`.
    *   La clé `API_KEY` pour la communication interne est gérée par [`docker-compose.yml`](docker-compose.yml:0).

### Méthode Manuelle (Pour Développement)
*   **Gestion des Dépendances :**
    *   Backend : [`requirements.txt`](backend/requirements.txt:0) (géré via `pip` dans un `venv`).
    *   Frontend : `package.json` (géré via `npm`).
*   **Variables d'Environnement (Installation Manuelle) :**
    *   [`backend/.env`](backend/.env.example:0) : Utilisé par `pydantic-settings` dans [`backend/config.py`](backend/config.py:1) pour charger les clés API des LLM et la `API_KEY` de CyberPlume.
    *   [`frontend/.env`](frontend/.env.example:0) : Utilisé par Vite pour `VITE_API_KEY` et `VITE_API_URL`.
*   **Lancement Manuel :**
    *   Backend : `source venv/bin/activate && uvicorn backend.main:app --reload --port 8080 --log-config log_config.yaml`.
    *   Frontend : `npm run dev` (dans le dossier `frontend/`).
*   **Tests Backend :** `pytest`. Configuration via [`backend/tests/conftest.py`](backend/tests/conftest.py:0).

## Outils et Pratiques
*   **Contrôle de Version :** Git.
*   **Documentation API :** Génération automatique par FastAPI (`/docs`, `/redoc`).
*   **Documentation Externe & Recherche d'Informations :**
    *   **`Context7` : Fortement recommandé.**
*   **Gestion Asynchrone :** Utilisation correcte de `async/await` dans FastAPI.

*Ce document est basé sur les technologies et outils listés ou mentionnés dans `docs/plan-cyber-plume.md` et l'état actuel du projet.*