# Plan d'Initialisation Git/GitHub et Dockerisation (Développement)

## 1. Initialisation de Git et Publication sur GitHub

**Objectif :** Mettre le projet CyberPlume sous contrôle de version avec Git et le publier sur un dépôt GitHub distant.

**Étapes prévues :**

1.  **Initialisation du dépôt Git local :**
    *   Exécuter la commande `git init` à la racine du projet `/mnt/serveur/serveur/cyberplume`.
2.  **Ajout des fichiers au suivi :**
    *   Exécuter `git add .`.
3.  **Premier commit :**
    *   Exécuter `git commit -m "Initial commit: Project setup, GitHub preparation, and style analysis fix"`.
4.  **Création du dépôt distant sur GitHub :**
    *   À réaliser manuellement sur la plateforme GitHub.
5.  **Liaison du dépôt local au dépôt distant :**
    *   Exécuter `git remote add origin <URL_DU_DEPOT_GITHUB>`.
6.  **Publication (Push) du code :**
    *   Exécuter `git push -u origin main` (ou `master`).
7.  **Tests Post-Publication (Crucial) :**
    *   Cloner le dépôt dans un nouvel environnement.
    *   Suivre les instructions du `README.md` pour l'installation et le lancement.
    *   Vérifier la fonctionnalité de l'application.
    *   Exécuter les tests backend (`pytest`).

## 2. Planification de la Dockerisation de CyberPlume (Mode Développement avec Vite)

**Objectif :** Définir une stratégie pour conteneuriser les applications backend (FastAPI) et frontend (Vue.js en mode développement avec Vite) de CyberPlume à l'aide de Docker, afin de simplifier le déploiement de développement et d'assurer la cohérence des environnements.

```mermaid
graph TD
    subgraph Docker Host
        subgraph Docker Compose Orchestration
            DC[docker-compose.yml]
        end

        subgraph Backend Service (FastAPI)
            BF[Dockerfile.backend] --> BI[Image Backend Python] --> BC[Conteneur Backend]
            BC -- Port 8080 --> HostPortB[Host Port 8080]
            BC -- Mounts --> DBVol[Volume BD (instance/cyberplume.db)]
            BC -- Mounts Code --> BackendCode[Code Source Backend]
            BC -- Reads --> EnvB[Fichier .env Backend]
        end

        subgraph Frontend Service (Vite Dev Server)
            FF[Dockerfile.frontend-dev] --> FI[Image Frontend Node] --> FC[Conteneur Frontend Dev]
            FC -- Port 5173 --> HostPortF[Host Port 5173]
            FC -- Mounts Code --> FrontendCode[Code Source Frontend]
            FC -- Reads --> EnvF[Fichier .env Frontend]
            FC -- Proxies API calls to --> BC
        end

        DC --> BF
        DC --> FF
        DC -- Manages --> BC
        DC -- Manages --> FC
        DC -- Defines --> DBVol
    end

    User[Utilisateur] -- HTTP (localhost:5173) --> HostPortF
    User[Utilisateur] -- HTTP (localhost:8080 - direct API si besoin) --> HostPortB
```

### a. Dockerfile pour le Backend (FastAPI) - `Dockerfile.backend`

1.  **Image de base :** `python:3.11-slim`.
2.  **Répertoire de travail :** `/app`.
3.  **Installation des dépendances :** Copier `backend/requirements.txt`, puis `pip install --no-cache-dir -r requirements.txt`.
4.  **Copie du code source :** Copier `backend/` dans `/app/backend/`.
5.  **Exposition du port :** `8080`.
6.  **Commande de démarrage :** `CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]`.

### b. Dockerfile pour le Frontend (Mode Développement Vite) - `Dockerfile.frontend-dev`

1.  **Image de base :** `node:lts-alpine`.
2.  **Répertoire de travail :** `/app`.
3.  **Installation des dépendances :** Copier `frontend/package.json` et `frontend/package-lock.json`, puis `npm install`.
4.  **Copie du code source :** Copier `frontend/` dans `/app/`.
5.  **Exposition du port :** `5173`.
6.  **Commande de démarrage :** `CMD ["npm", "run", "dev"]` (s'assurer que le script `dev` dans `package.json` inclut `vite --host 0.0.0.0` ou que Vite le fait par défaut).

### c. Fichier `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8080:8080"
    volumes:
      - ./instance:/app/instance # Persistance de la base de données
      - ./backend:/app/backend   # Montage du code source pour le hot-reload
    env_file:
      - ./backend/.env
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend-dev
    ports:
      - "5173:5173" # Port par défaut de Vite
    volumes:
      - ./frontend:/app # Montage du code source pour le hot-reloading
      - /app/node_modules # Cache des node_modules du conteneur
    depends_on:
      - backend
    env_file:
      - ./frontend/.env # Pour VITE_API_KEY et VITE_API_URL
    restart: unless-stopped
```

### Points d'attention pour la dockerisation en mode développement :

*   **Configuration du proxy Vite :**
    *   Dans `frontend/vite.config.js`, le proxy (`server.proxy`) doit cibler `http://backend:8080`.
    *   Le fichier `frontend/.env` (utilisé par le conteneur `frontend`) devra avoir : `VITE_API_URL=http://backend:8080`.
*   **Montage de volumes pour le code source :** Essentiel pour le hot-reloading.
*   **`node_modules` :** Le volume `- /app/node_modules` pour le service frontend est important.
*   **Fichiers `.env` :** Doivent être correctement configurés et présents pour `env_file`.