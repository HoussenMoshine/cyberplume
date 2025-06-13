# Plan de la Fonctionnalité de Contexte du Chapitrage

**Objectif :** Implémenter une première version de la gestion du contexte inter-chapitres pour améliorer l'assistance IA, en commençant par l'approche la plus simple et la plus efficace.

**Contexte Actuel :**
*   Branche Git : `approche-contexte`
*   Le document `banque-memoire/approches-contexte-chapitre.md` décrit quatre approches principales : Résumés de Chapitres Précédents, Base de Connaissances Dynamique, Extraction d'Entités et de Faits Clés Structurés, et Récupération Augmentée par Génération (RAG).
*   Le document recommande de commencer par une MVP (Minimum Viable Product) et de privilégier l'approche 1 (Résumés de Chapitres Précédents) pour sa simplicité relative.

**Approche Choisie (MVP) :** **Approche 1: Résumés de Chapitres Précédents**

Cette approche est la plus directe et permet de fournir un contexte narratif sans introduire une complexité excessive dès le départ.

**Étapes Détaillées du Plan :**

```mermaid
graph TD
    A[Démarrage] --> B{Analyse Approfondie de l'Approche 1};
    B --> C[Modification du Modèle de Données Chapter];
    C --> D[Création de la Route API de Génération de Résumé];
    D --> E[Implémentation du Service de Génération de Résumé (Backend)];
    E --> F[Intégration Frontend (Bouton & Affichage Résumé)];
    F --> G[Modification de l'Injection du Contexte dans les Prompts IA];
    G --> H[Tests & Validation];
    H --> I[Mise à Jour de la Banque de Mémoire];
    I --> J[Présentation du Plan à l'Utilisateur];
```

**Détail des Étapes :**

1.  **Analyse Approfondie de l'Approche 1 (Résumés de Chapitres Précédents) :**
    *   Relire spécifiquement la section "Approche 1" dans `banque-memoire/approches-contexte-chapitre.md` pour s'assurer de bien comprendre toutes les implications.
    *   Identifier les fichiers backend et frontend existants qui seront affectés.

2.  **Modification du Modèle de Données `Chapter` (Backend) :**
    *   Ajouter un nouveau champ `summary` de type `TEXT` (nullable) au modèle SQLAlchemy `Chapter` dans `backend/models.py`.
    *   Mettre à jour le schéma Pydantic correspondant pour inclure ce champ.
    *   Préparer une migration de base de données si nécessaire (bien que pour SQLite, une simple recréation de la DB en dev puisse suffire si les données ne sont pas critiques, mais une migration est la bonne pratique).

3.  **Création de la Route API de Génération de Résumé (Backend) :**
    *   Créer une nouvelle route API dans un routeur existant (ex: `backend/routers/chapters.py` ou un nouveau `backend/routers/summaries.py`) pour `POST /api/chapters/{chapter_id}/generate-summary`.
    *   Cette route recevra l'ID du chapitre et déclenchera la génération du résumé.

4.  **Implémentation du Service de Génération de Résumé (Backend) :**
    *   Dans le backend, créer une fonction ou un service qui :
        *   Récupère le contenu textuel complet du chapitre spécifié par `chapter_id`.
        *   Nettoie le contenu HTML si nécessaire (utiliser `backend/utils/text_extractor.py`).
        *   Appelle un service IA (via l'adaptateur existant dans `backend/ai_services/`) avec un prompt de summarisation.
        *   Sauvegarde le résumé généré dans le nouveau champ `summary` du chapitre dans la base de données.
    *   Considérer l'exécution asynchrone de cette tâche pour ne pas bloquer l'interface utilisateur.

5.  **Intégration Frontend (Bouton & Affichage Résumé) :**
    *   Ajouter un bouton "Générer/Mettre à jour le résumé" dans l'interface utilisateur, probablement dans le composant de gestion de chapitre ou l'éditeur (ex: `frontend/src/components/ChapterListItem.vue` ou `frontend/src/components/EditorComponent.vue`).
    *   Permettre à l'utilisateur de visualiser le résumé généré, et potentiellement de l'éditer manuellement. Cela pourrait être un nouveau champ dans un dialogue d'édition de chapitre ou une section dédiée.

6.  **Modification de l'Injection du Contexte dans les Prompts IA (Backend) :**
    *   Identifier les routes API backend qui appellent les services IA pour la génération/suggestion de texte (ex: `backend/routers/analysis.py`, `backend/routers/scenes.py` ou un routeur IA plus général).
    *   Modifier la logique pour récupérer le résumé du chapitre précédent (N-1) lorsque l'IA est sollicitée pour le chapitre actuel (N).
    *   Intégrer ce résumé dans le prompt système envoyé à l'IA, en suivant l'exemple fourni dans le document `banque-memoire/approches-contexte-chapitre.md`.

7.  **Tests & Validation :**
    *   Tester la génération de résumés : vérifier que le résumé est bien généré et sauvegardé.
    *   Tester l'injection du contexte : vérifier que l'IA reçoit bien le résumé du chapitre précédent et que cela influence positivement ses réponses.
    *   Tester l'interface utilisateur : vérifier que le bouton et l'affichage du résumé fonctionnent comme prévu.

8.  **Mise à Jour de la Banque de Mémoire :**
    *   Mettre à jour `banque-memoire/activeContext.md` et `banque-memoire/progress.md` pour refléter l'avancement de cette fonctionnalité.