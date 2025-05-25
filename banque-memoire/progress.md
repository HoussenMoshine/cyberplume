# Progression - CyberPlume (Mise à jour : 25/05/2025 - 08:05)

## Ce qui Fonctionne (État Actuel)

### Backend & Frontend (en environnement Docker)
*   **Communication de base rétablie :** Les erreurs 404 dues aux `net::ERR_NAME_NOT_RESOLVED` (causées par des redirections 307 avec slashs finaux) ont été corrigées pour les fonctionnalités principales.
*   **Chargement des Données :**
    *   Liste des projets.
    *   Liste des chapitres par projet.
    *   Contenu des chapitres dans l'éditeur.
*   **Fonctionnalités CRUD de base (testées par l'utilisateur) :**
    *   Ajout/suppression de projets.
    *   Ajout/suppression de chapitres.
    *   Gestion des scènes (création/affichage).
    *   Gestion des personnages (création/affichage).
*   **Actions IA de base :**
    *   Les fonctions IA de base (ex: "Continuer" via `ActionPanel`) sont de nouveau opérationnelles après correction d'une erreur JavaScript (`triggerContinueFromComposable is not a function`).
*   **Modèle spaCy :** Le backend semble tenter de charger `fr_core_news_sm` (d'après les logs `WARNING:root:Modèle 'fr_core_news_md' non trouvé. Tentative avec 'fr_core_news_sm'.`), ce qui indique que l'ajout au Dockerfile a eu un effet. Son utilisation effective reste à valider via les fonctionnalités d'analyse.

### Configuration & Outillage (État après corrections)
*   Proxy Vite ([`frontend/vite.config.js`](frontend/vite.config.js:1)) : Fonctionne avec `VITE_PROXY_API_TARGET_URL=http://backend:8080` et réécriture de `/api`.
*   Fichiers de Dockerisation ([`Dockerfile.backend`](Dockerfile.backend:1), [`Dockerfile.frontend-dev`](Dockerfile.frontend-dev:1), [`docker-compose.yml`](docker-compose.yml:1)) : Intègrent les corrections pour spaCy et la configuration du proxy.
*   Appels API Frontend : Corrigés dans `useProjects.js`, `useChapters.js`, `useChapterContent.js` pour ne plus utiliser de slashs finaux problématiques.
*   Composable `useAIActions.js` : Fonctions correctement exportées et utilisées.
*   Routeur Backend `projects.py` : Préfixe `/api` supprimé pour éviter conflit avec le proxy.

## Ce qui Reste à Construire / Améliorer (Prochaine Session)

*   **Résoudre Erreurs 404 pour les Analyses (Priorité Haute) :**
    *   **Analyse de contenu de chapitre :** `POST /api/chapters/{id}/analyze-content` retourne 404.
        *   Vérifier l'appel dans [`frontend/src/composables/useAnalysis.js`](frontend/src/composables/useAnalysis.js:1) (slash final, chemin exact).
        *   Vérifier le routeur [`backend/routers/analysis.py`](backend/routers/analysis.py:1) (absence de préfixe `/api` si géré par proxy, définition de la route).
    *   **Analyse de cohérence de projet :** `POST /analyze/consistency` retourne 404.
        *   Vérifier l'appel dans [`frontend/src/composables/useAnalysis.js`](frontend/src/composables/useAnalysis.js:1).
        *   Vérifier le routeur [`backend/routers/analysis.py`](backend/routers/analysis.py:1).
*   **Valider le fonctionnement complet de spaCy :** Une fois les routes d'analyse ci-dessus corrigées, tester intensivement ces fonctionnalités.
*   **(Observation/Optionnel) Redirections `/api/characters` :**
    *   Les logs backend montrent encore des redirections 307 pour `/api/characters` vers `/api/characters/`. Bien que cela semble fonctionner, envisager de :
        *   Supprimer le préfixe `/api` du routeur [`backend/routers/characters.py`](backend/routers/characters.py:1) s'il existe.
        *   S'assurer que les appels frontend (probablement `useCharacters.js`) se font vers `/api/characters` (sans slash final).
*   **(Observation/Optionnel) Appel `/api-keys-config/status` :**
    *   Vérifier la cohérence entre l'appel frontend et la définition du routeur [`backend/routers/api_keys_config.py`](backend/routers/api_keys_config.py:1) (préfixe `/api`, slash final).
*   **Optimisation Docker (Post-Fonctionnalité) :**
    *   Envisager des stratégies pour réduire les temps de reconstruction des images Docker lors du développement (ex: montage plus fin des volumes pour le code source).
*   **Tests Fonctionnels Complets :** Effectuer des tests exhaustifs de toutes les fonctionnalités de l'application fonctionnant sous Docker une fois les problèmes d'analyse résolus.
*   **Documentation :** Mettre à jour [`README.md`](README.md) avec les instructions de lancement via Docker.
*   **Commit et Push** des changements de la branche `dockerisation`.
*   **Révocation et Remplacement des Clés API Exposées (Action Externe Critique - Rappel).**

## Problèmes Actuels (État Actuel)

*   **Erreur 404 :** `POST /api/chapters/{id}/analyze-content` (lors de l'analyse de contenu d'un chapitre).
*   **Erreur 404 :** `POST /analyze/consistency` (lors de l'analyse de cohérence d'un projet).
*   **(Mineur/Observation) Redirections 307 :** Pour les appels à `/api/characters` dans les logs backend, bien que la fonctionnalité semble opérationnelle.

## Évolution des Décisions

### Session 25 Mai
*   **Objectif :** Rétablir la communication frontend-backend en environnement Docker.
*   Correction itérative des problèmes de slashs finaux dans les appels API frontend (`useProjects.js`, `useChapters.js`, `useChapterContent.js`) pour résoudre les erreurs `net::ERR_NAME_NOT_RESOLVED` causées par des redirections 307.
*   Correction d'une erreur JavaScript dans `useAIActions.js` et `EditorComponent.vue` concernant l'appel de `triggerContinueFromComposable`.
*   Suppression du préfixe `/api` dans le routeur `projects.py` pour alignement avec le proxy Vite.
*   Validation du fonctionnement de base (CRUD projets/chapitres, contenu chapitres, actions IA de base).
*   Identification des erreurs 404 pour les fonctionnalités d'analyse comme prochains points à traiter.
*   Décision de mettre à jour la Banque de Mémoire et de ne pas corriger les erreurs d'analyse dans la session actuelle.

*(Les détails des sessions antérieures sont conservés dans activeContext.md)*