# Plan de Préparation (Révisé v2) pour la Publication de CyberPlume sur GitHub

```mermaid
graph TD
    AA[Début de la Préparation GitHub] --> AB{Étape 1: Vérification et Finalisation des Dépendances};
    AB --> AC[Backend: Vérifier l'exhaustivité de backend/requirements.txt];
    AB --> AD[Backend: Mettre à jour backend/requirements.txt si nécessaire];
    AB --> AE[Frontend: Vérifier l'exhaustivité de frontend/package.json];
    AB --> AF[Frontend: Mettre à jour frontend/package.json si nécessaire (ex: npm install <pkg> --save)];

    AF --> B{Étape 2: Gestion des Fichiers Ignorés (.gitignore)};
    B --> C[Identifier les fichiers à ignorer pour le Backend Python];
    B --> D[Identifier les fichiers à ignorer pour le Frontend Node.js/Vue.js];
    B --> E[Créer/Mettre à jour backend/.gitignore];
    B --> F[Créer/Mettre à jour frontend/.gitignore];
    B --> G[Optionnel: Créer/Mettre à jour .gitignore à la racine du projet];
    
    G --> H{Étape 3: Vérification des Informations Sensibles};
    H --> I[Examiner backend/.env et s'assurer qu'il est ignoré];
    H --> J[Fournir un backend/.env.example (sans clés)];
    H --> K[Examiner frontend/.env et s'assurer qu'il est ignoré];
    H --> L[Fournir un frontend/.env.example (sans clés)];
    H --> M[Vérifier l'absence de clés hardcodées dans le code source];
    
    M --> N{Étape 4: Création du Fichier README.md (Détaillé & Pédagogique)};
    N --> NA[Préparer l'image: Copier `frontend/src/assets/livre.svg` vers `docs/assets/logo.svg`];
    N --> O[Créer README.md à la racine du projet];
    N --> NB[Intégrer l'image `docs/assets/logo.svg` au début du README.md];
    N --> P[Rédiger la section: Description du Projet (CyberPlume)];
    N --> P1[Rédiger la section: Fonctionnalités Clés (détaillé, basé sur projectbrief.md)];
    N --> Q[Rédiger la section: Technologies Utilisées];
    N --> R[Rédiger la section: Prérequis (Python, Node.js/npm, Git) avec instructions de vérification/installation pour Linux, Windows, macOS];
    N --> R1[Ajouter instruction: Clonage du dépôt (`git clone ...`)];
    N --> S[Rédiger la section: Instructions d'Installation Backend (détaillé pour Linux, Windows, macOS - venv, activation, pip install, .env)];
    N --> T[Rédiger la section: Instructions d'Installation Frontend (détaillé pour Linux, Windows, macOS - npm install, .env)];
    N --> U[Rédiger la section: Instructions de Lancement (Backend & Frontend, ordre, ports, URL d'accès)];
    N --> U1[Optionnel: Ajouter une section Dépannage pour les problèmes courants];
    N --> V[Optionnel: Ajouter Structure du Projet / Contribution];
    
    V --> W[Fin de la Préparation];
```

## Détail des Étapes :

### Étape 1 : Vérification et Finalisation des Dépendances
*   **Objectif :** S'assurer que tous les packages nécessaires sont correctement listés pour une installation reproductible.
*   **Actions envisagées :**
    1.  **Backend (`backend/requirements.txt`) :**
        *   Comparer la sortie de `pip freeze` (dans l'environnement virtuel activé du backend) avec le contenu actuel de `backend/requirements.txt`.
        *   Ajouter toute dépendance manquante. Il est souvent préférable de regénérer le fichier avec `pip freeze > backend/requirements.txt` après s'être assuré que l'environnement est propre et ne contient que les dépendances du projet.
    2.  **Frontend (`frontend/package.json`) :**
        *   Examiner les sections `dependencies` et `devDependencies`.
        *   Vérifier si des bibliothèques ont été installées globalement ou manuellement sans être sauvegardées dans `package.json` (par exemple, en oubliant `--save` ou `--save-dev`). Cela peut nécessiter une revue des `import` dans le code source frontend si un doute subsiste.

### Étape 2 : Gestion des Fichiers Ignorés (`.gitignore`)
*   **Objectif :** S'assurer que seuls les fichiers pertinents sont versionnés, en excluant les dépendances, les fichiers de configuration locaux, les fichiers compilés, et les bases de données locales.
*   **Actions envisagées :**
    1.  **Backend (`backend/.gitignore`) :**
        *   Inclure : `venv/`, `__pycache__/`, `*.pyc`, `*.log`, `instance/cyberplume.db`, `.env`.
    2.  **Frontend (`frontend/.gitignore`) :**
        *   Inclure : `node_modules/`, `dist/`, `.DS_Store`, `*.local`, `.env*` (sauf `.env.example`), `coverage/`.
    3.  **Racine du Projet (`./.gitignore`) :**
        *   Optionnel : Peut inclure des fichiers spécifiques à l'IDE comme `.vscode/` si les paramètres ne sont pas destinés à être partagés, ou des fichiers temporaires globaux.

### Étape 3 : Vérification des Informations Sensibles
*   **Objectif :** Prévenir la fuite de clés API ou d'autres secrets.
*   **Actions envisagées :**
    1.  **Fichiers `.env` :**
        *   Confirmer que `backend/.env` et `frontend/.env` sont bien listés dans leurs `.gitignore` respectifs.
        *   Créer des fichiers d'exemple : `backend/.env.example` et `frontend/.env.example`. Ces fichiers listeront les variables d'environnement nécessaires avec des valeurs vides ou des placeholders (ex: `GEMINI_API_KEY=VOTRE_CLE_ICI`).
    2.  **Code Source :**
        *   Re-vérifier que `backend/config.py` et `frontend/src/config.js` chargent correctement les variables d'environnement et ne contiennent aucune valeur par défaut sensible.
        *   Effectuer une recherche globale dans le code pour des motifs de clés API potentielles (ex: `AIza...`, `sk-...`, etc.) ou des termes comme "API_KEY", "SECRET" qui ne seraient pas gérés via les `.env`.

### Étape 4 : Création du Fichier `README.md` (Détaillé & Pédagogique)
*   **Objectif :** Fournir un guide extrêmement clair, détaillé et pédagogique pour permettre même aux novices d'installer et de lancer l'application sur différents systèmes d'exploitation (Linux, Windows, macOS). Mettre en avant les fonctionnalités.
*   **Actions envisagées :**
    1.  **Préparation de l'image :** Copier l'image `frontend/src/assets/livre.svg` depuis son emplacement actuel vers `docs/assets/logo.svg` (créer le dossier `docs/assets/` si besoin).
    2.  Créer le fichier `README.md` à la racine du projet.
    3.  **Intégration de l'image :** Utiliser la syntaxe Markdown pour afficher l'image au début du `README.md`, avec un chemin relatif (ex: `![CyberPlume Logo](./docs/assets/logo.svg)`).
    4.  **Section Fonctionnalités Clés :**
        *   Détailler les fonctionnalités en s'appuyant sur `projectbrief.md` et `productContext.md`.
        *   Exemples :
            *   Interface d'Écriture & Assistance IA (Éditeur TipTap, Sauvegarde, Génération IA, Manipulation IA).
            *   Gestion de Projet d'Écriture (Organisation Projets/Chapitres/Scènes, Métadonnées, Gestion des Personnages).
            *   Intégration IA Configurable (Multi-Fournisseurs, Sélection dynamique).
            *   Export & Partage (Formats multiples).
    5.  **Section Prérequis :**
        *   Pour Python, Node.js/npm, et Git :
            *   Comment vérifier s'ils sont installés.
            *   Liens vers les sites officiels pour le téléchargement.
            *   Versions recommandées/minimales.
            *   Instructions spécifiques si des commandes diffèrent légèrement entre OS (ex: `python` vs `python3`).
    6.  **Section Clonage du Dépôt :**
        *   Ajouter `git clone https://github.com/VOTRE_UTILISATEUR/NOM_DU_DEPOT.git` (en indiquant de remplacer par l'URL réelle).
    7.  **Instructions d'Installation Backend & Frontend :**
        *   Pour chaque étape (création/activation `venv`, copie/remplissage `.env`, installation dépendances) :
            *   Fournir les commandes exactes pour Linux/macOS (bash/zsh).
            *   Fournir les commandes exactes pour Windows (PowerShell et/ou CMD).
            *   Insister sur l'importance de remplir correctement les fichiers `.env` avec les clés API personnelles et les configurations d'URL.
    8.  **Instructions de Lancement :**
        *   Préciser l'ordre (backend d'abord).
        *   Mentionner les ports par défaut et comment accéder à l'application.
    9.  **Section Dépannage (Fortement Recommandé) :**
        *   Anticiper les problèmes courants :
            *   "Port déjà utilisé" : comment identifier et changer le port si nécessaire.
            *   Erreurs liées aux clés API (mauvaises clés, non fournies).
            *   Oubli d'activation de l'environnement virtuel Python.
            *   Problèmes de proxy ou de CORS (bien que le proxy Vite devrait gérer cela en dev).
            *   Permissions de fichiers/dossiers.