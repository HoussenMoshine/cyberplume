# **Plan de Développement de CyberPlume**

Instructions pour le développement : Pour vous assurer d'utiliser les documentations les plus récentes, utilisez context7.

## **1. Architecture Technique**

### Backend

-   **Framework** : **FastAPI** (léger, asynchrone, idéal pour les API IA)
-   **Base de données** : **SQLite** (fichier local, pas de serveur requis)
-   **ORM** : SQLAlchemy
-   **Validation** : Pydantic
-   **Environnement** : `venv` (Python 3.11+)

### Frontend

-   **Framework** : **Vue.js 3** (approche progressive, simple pour une app locale)
-   **Bibliothèques Principales** :
    -   **TipTap 2** (éditeur de texte riche intégré)
    -   **Vuetify 3** (composants Material Design)
    -   `axios` (Requêtes HTTP)

---

## **2. Structure du Projet (Conceptuelle)**

```
cyberplume/
├── backend/            # API FastAPI
│   ├── main.py         # Point d'entrée, routers, config
│   ├── models.py       # Modèles SQLAlchemy & Pydantic (Projets, Chapitres, Personnages, Scènes)
│   ├── crud.py         # Logique base de données
│   ├── routers/        # Routes API par fonctionnalité (projets, ai, export, etc.)
│   └── ai_services/    # Adapters pour Gemini, Mistral, OpenRouter, etc.
│
├── frontend/           # App Vue.js
│   ├── src/
│   │   ├── components/ # Éditeur, Gestionnaire Projets, Gestionnaire Personnages, Barre Outils IA, etc.
│   │   ├── services/   # Logique API frontend
│   │   └── views/      # Pages/Vues principales
│   └── package.json
│
└── instance/           # Données locales (ignoré par git)
    └── cyberplume.db   # Base SQLite
```

---

## **3. Fonctionnalités Principales**

### **a. Interface d'Écriture & Assistance IA**

-   **Éditeur de Texte Riche (TipTap)** : Intégration d'un éditeur WYSIWYG moderne.
-   **Sauvegarde du Contenu** : Mécanismes de sauvegarde automatique et manuelle.
-   **Assistance IA Contextuelle** :
    -   **Génération de Texte** :
        -   "Continuer" : Complétion intelligente du texte en cours.
        -   "Suggérer" : Génération de texte libre basée sur le contexte.
        -   "Dialogue" : Aide à la création et à la poursuite de dialogues.
    -   **Manipulation de Texte** :
        -   "Reformuler" : Proposer des alternatives pour une sélection de texte.
        -   "Raccourcir" : Condenser une sélection de texte.
        -   "Étendre" / "Développer" : Élaborer une sélection de texte.
    -   **Aide à la Création de Contenu Spécifique** :
        -   **Personnages** : Génération de noms, suggestion de traits de caractère, développement de backstories.
        -   **Scènes** : Description d'ambiance, suggestion de détails sensoriels, génération d'ébauches de scènes.

### **b. Gestion de Projet d'Écriture**

-   **Organisation Hiérarchique** :
    -   Gestion des **Projets** (CRUD).
    -   Gestion des **Chapitres** au sein des projets (CRUD, ordonnancement).
    -   Gestion des **Scènes** au sein des chapitres (CRUD, organisation).
-   **Métadonnées** :
    -   Attribution de métadonnées aux chapitres (ex: Statut, Point de Vue, Timeline).
    -   Attribution de métadonnées aux scènes.
-   **Gestion des Éléments Narratifs** :
    -   Gestion dédiée des **Personnages** (CRUD, fiches détaillées: description, traits, backstory, notes, relations).
    -   Liaison des personnages aux projets, chapitres et scènes.
-   **Suivi & Analyse** :
    -   **Tableau de Bord** : Vue d'ensemble de la progression (ex: comptage de mots par projet/chapitre).
    -   **Analyse de Cohérence** : Outils basiques pour vérifier la cohérence narrative (ex: utilisation des personnages, timeline).

### **c. Intégration IA Configurable**

-   **Support Multi-Fournisseurs IA** : Architecture modulaire (Adapters/Factory) pour intégrer divers services (Gemini, Mistral, OpenRouter, et potentiellement d'autres).
-   **Sélection Dynamique** : Interface pour choisir le fournisseur d'IA et le modèle spécifique à utiliser.
-   **Personnalisation du Style IA** : Option pour guider le ton ou le style de l'écriture générée par l'IA.
-   **Paramètres Avancés IA** : Contrôle utilisateur sur des paramètres comme la "température" (créativité) et la longueur maximale des réponses.

### **d. Export & Partage**

-   **Formats d'Export Multiples** : Génération de documents aux formats :
    -   DOCX
    -   PDF
    -   TXT
    -   EPUB
    -   ODT
    -   Markdown
-   **Niveaux d'Export** :
    -   Export d'un **chapitre individuel**.
    -   Export d'un **projet complet** (compilation des chapitres ordonnés).
-   **Bibliothèques Cibles** : Utilisation de bibliothèques comme `python-docx`, `xhtml2pdf`/`reportlab`, `ebooklib`, `html2text`, et potentiellement des convertisseurs pour ODT/Markdown.

---

## **4. Domaines de Développement Clés**

### **Backend (API FastAPI)**

1.  **Fondations** : Mise en place du serveur, configuration, gestion base de données, CORS.
2.  **API CRUD** : Routes pour la gestion complète des Projets, Chapitres, Personnages, Scènes.
3.  **API IA** :
    -   Route générique `/generate` acceptant contexte, action souhaitée, paramètres (fournisseur, modèle, style, température, etc.).
    -   Route `/models` pour lister les modèles disponibles par fournisseur.
    -   Implémentation des adaptateurs spécifiques à chaque service IA.
4.  **API Export** : Routes pour générer et servir les fichiers d'export (chapitre et projet complet) dans les différents formats.
5.  **API Analyse** : Route pour l'analyse de cohérence (via `spaCy` ou autre).
6.  **Authentification** : Mécanisme d'authentification (ex: clé API locale).

    ```python
    # Concept: Factory pour les services IA
    def get_ai_service(provider: str, api_key: str):
        # Logique pour instancier le bon adapter (Gemini, Mistral...)
        pass
    ```

### **Frontend (Application Vue.js)**

1.  **Interface Principale** : Structure de l'application, vues principales, navigation.
2.  **Composant Éditeur** : Intégration TipTap, gestion du contenu, interaction avec l'API de sauvegarde.
3.  **Composant Gestionnaire de Projet** : Affichage hiérarchique (Projets > Chapitres > Scènes), actions CRUD, sélection, gestion des métadonnées.
4.  **Composant Gestionnaire de Personnages** : Interface dédiée pour créer, lister, éditer les personnages et leurs détails.
5.  **Composant Barre d'Outils IA** : Sélection fournisseur/modèle/style, réglage paramètres avancés, boutons pour les actions IA globales.
6.  **Intégration Actions IA** : Connexion des boutons (toolbar, BubbleMenu) aux appels API `/generate`, affichage des résultats/suggestions.
7.  **Intégration Export** : Connexion des boutons d'export aux appels API, gestion du téléchargement des fichiers.
8.  **Feedback Utilisateur** : Indicateurs de chargement, messages d'erreur/succès (`v-snackbar`).

    ```vue
    <!-- Concept: Composant Gestion Personnages -->
    <template>
      <v-container>
        <v-list> <!-- Liste des personnages --> </v-list>
        <v-btn @click="showCreateCharacterDialog = true">Nouveau Personnage</v-btn>
        <v-dialog v-model="showCharacterDetailsDialog">
           <!-- Formulaire détaillé pour un personnage avec champs et boutons IA -->
           <v-text-field label="Nom"></v-text-field>
           <v-textarea label="Description"></v-textarea>
           <v-btn @click="generateBackstory(character)">Générer Backstory</v-btn>
        </v-dialog>
      </v-container>
    </template>
    ```

### **Fonctionnalités Transverses & Optimisations**

1.  **Logique d'Export** : Implémentation des conversions de format (HTML vers DOCX, PDF, EPUB, etc.).
2.  **Intégration NLP** : Utilisation de `spaCy` ou similaire pour l'analyse de texte côté backend.
3.  **Caching** : Mise en place d'un cache local pour les réponses IA identiques.
4.  **Mode Hors-ligne** : Stratégie pour permettre l'édition sans connexion et synchronisation ultérieure.
5.  **Thème Sombre** : Support d'un thème alternatif pour l'interface.

---

## **5. Technologies Complémentaires Envisagées**

-   **NLP** : `spaCy` pour l'analyse de cohérence et potentiellement d'autres tâches linguistiques.
-   **Authentification** : `HTTP Basic Auth` ou système basé sur une clé API locale pour la simplicité.
-   **Déploiement** : Fichier `docker-compose.yml` pour faciliter le lancement local ou le déploiement.

---

## **6. Documentation Cible**

-   **Guide d'Installation et de Configuration** : Instructions claires pour mettre en place l'environnement de développement et lancer l'application.
    ```bash
    # Exemple commandes installation
    python -m venv venv
    source venv/bin/activate # ou venv\Scripts\activate sur Windows
    pip install -r backend/requirements.txt
    cd frontend
    npm install
    # Lancement (exemple)
    # Terminal 1: cd backend && uvicorn main:app --reload
    # Terminal 2: cd frontend && npm run dev
    ```
-   **Guide Utilisateur** : Documentation fonctionnelle expliquant comment utiliser les différentes fonctionnalités de CyberPlume.
-   **Documentation API** : Documentation générée par FastAPI (`/docs`, `/redoc`) et potentiellement complétée manuellement.
-   **Documentation Technique** : Notes sur l'architecture, les décisions de conception importantes, et le fonctionnement interne pour les développeurs.

---