# Contexte Technique - CyberPlume (Mise à jour : 20/05/2025 - 07:23)

## Technologies Principales

### Backend

*   **Langage :** Python (3.11+)
*   **Framework Web :** FastAPI
*   **Base de Données :** SQLite (via fichier local `instance/cyberplume.db`)
*   **ORM :** SQLAlchemy
*   **Validation des Données (API) :** Pydantic
*   **Environnement Virtuel :** `venv`

### Frontend

*   **Langage :** JavaScript (ES6+)
*   **Framework :** Vue.js 3 (utilisant la Composition API)
*   **Bibliothèque UI :** Vuetify 3 (pour les composants Material Design)
*   **Éditeur de Texte Riche :** TipTap 2
*   **Client HTTP :** `axios` (pour les appels API vers le backend)
*   **Gestionnaire de Paquets :** npm
*   **Outil de Build :** Vite.
    *   Utilise un serveur proxy en développement ([`frontend/vite.config.js`](frontend/vite.config.js:1)) pour rediriger les appels `/api/*` vers le backend FastAPI (ex: port 8080) avec réécriture de chemin pour supprimer le préfixe `/api`.

## Bibliothèques et Services Clés

### Backend

*   **Intégration IA :**
    *   Bibliothèques spécifiques aux fournisseurs (ex: `google-generativeai`, `mistralai` (v1.7.0), `openai` (v1.78.1) pour OpenRouter).
*   **Export :**
    *   `python-docx` (pour DOCX)
    *   `xhtml2pdf` ou `reportlab` (pour PDF)
    *   `ebooklib` (pour EPUB)
    *   `html2text` (pour TXT/Markdown)
*   **Traitement du Langage Naturel (NLP) :**
    *   `spaCy` (utilisé pour l'analyse de cohérence/contenu)
    *   `beautifulsoup4` (utilisé pour l'extraction de texte brut avant analyse)
*   **Serveur ASGI :** Uvicorn (utilisé pour lancer FastAPI en développement, typiquement sur le port 8080).

### Frontend

*   **Composants Vuetify :** Utilisation extensive. Configuration du thème dans `src/plugins/vuetify.js`.
*   **TipTap Extensions :** Extensions de base et potentiellement personnalisées.
*   **Icônes (Bibliothèque) :** `@tabler/icons-vue` pour les icônes génériques.
*   **Icônes (Personnalisées) :** Fichiers SVG stockés dans [`frontend/src/assets/`](frontend/src/assets/) et intégrés via des balises `<img>` avec import de l'URL du fichier.
*   **Configuration Globale :** [`frontend/src/config.js`](frontend/src/config.js:1) charge la configuration de l'application, y compris `apiKey` (via `VITE_API_KEY`) et `apiUrl`.

## Configuration de Développement

*   **Gestion des Dépendances :**
    *   Backend : [`requirements.txt`](backend/requirements.txt) (géré via `pip`).
    *   Frontend : `package.json` (géré via `npm`).
*   **Variables d'Environnement :**
    *   [`backend/.env`](backend/.env) : Utilisé par `pydantic-settings` dans [`backend/config.py`](backend/config.py:1) pour charger les clés API des fournisseurs LLM (ex: `GEMINI_API_KEY`, `MISTRAL_API_KEY`) et la clé API de l'application CyberPlume (`API_KEY`).
    *   [`frontend/.env`](frontend/.env) : Utilisé par Vite pour charger les variables d'environnement préfixées par `VITE_` (ex: `VITE_API_KEY` pour la clé d'authentification frontend-backend, `VITE_API_URL`).
*   **Lancement :**
    *   Backend : `source venv/bin/activate && uvicorn backend.main:app --reload --port 8080` (port 8080 confirmé).
    *   Frontend : `npm run dev` (dans le dossier `frontend/`).
*   **Tests Backend :** `pytest`. Configuration via [`backend/tests/conftest.py`](backend/tests/conftest.py).

## Outils et Pratiques

*   **Contrôle de Version :** Git.
*   **Documentation API :** Génération automatique par FastAPI (`/docs`, `/redoc`).
*   **Documentation Externe & Recherche d'Informations :**
    *   **`Context7` : Fortement recommandé.**
*   **Gestion Asynchrone :** L'utilisation correcte de `async/await` est cruciale dans FastAPI et lors de l'interaction avec des bibliothèques IA asynchrones pour éviter les problèmes de boucle d'événements.
*   **Déploiement (Envisagé) :** Utilisation de Docker et `docker-compose.yml`.

*Ce document est basé sur les technologies et outils listés ou mentionnés dans `docs/plan-cyber-plume.md` et l'état actuel du projet.*