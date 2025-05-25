# Progression - CyberPlume (Mise à jour : 24/05/2025 - 07:18)

## Ce qui Fonctionne (État Actuel)

### Backend
*   API CRUD : Gestion complète (Création, Lecture, Mise à jour, Suppression) pour Projets, Chapitres, Personnages fonctionnelle (testé en dehors de Docker).
*   Réordonnancement : API pour réorganiser les chapitres (`/reorder`) opérationnelle (testé en dehors de Docker).
*   API IA Générale (`/generate/text`) et Génération Personnage (`/api/characters/generate`) : Fonctionnelles avec gestion des clés API DB/fallback .env (testé en dehors de Docker).
*   API Export, Analyse Cohérence, Modèles IA, Analyse Style : Fonctionnelles (testé en dehors de Docker).
*   Architecture IA, Base de Données, Configuration `config.py`, Sécurité (chiffrement clés), Gestion Clés API Fournisseurs : Stables (testé en dehors de Docker).
*   *Note : La correction pour le modèle spaCy (ajout de `RUN python -m spacy download fr_core_news_sm` dans [`Dockerfile.backend`](Dockerfile.backend:1)) a été préparée mais non validée par un build Docker réussi et test fonctionnel.*

### Frontend
*   Fonctionnalités de base de l'éditeur et gestion de projet : Stables (testé en dehors de Docker).
*   Gestion des Chapitres, Fournisseurs IA, Analyse Contenu/Style, Export, Gestion Clés API, Notifications : Fonctionnels (testé en dehors de Docker).
*   **Modifications pour Dockerisation :**
    *   Tous les appels API dans les fichiers composables (`useAIActions.js`, `useAIModels.js`, `useAnalysis.js`, `useChapterContent.js`, `useChapters.js`, `useProjects.js`, `useSceneContent.js`, `useScenes.js`) ont été modifiés pour utiliser des chemins relatifs commençant par `/api/`.
*   Le frontend se lance via Docker (selon le test utilisateur du 24/05), mais la communication avec le backend échoue (erreurs 404).

### Configuration & Outillage
*   Proxy Vite ([`frontend/vite.config.js`](frontend/vite.config.js:1)) : Configuration modifiée pour utiliser `VITE_PROXY_API_TARGET_URL` ou une valeur par défaut.
*   Fichiers de Dockerisation :
    *   [`Dockerfile.backend`](Dockerfile.backend:1) : Modifié pour inclure le téléchargement du modèle spaCy `fr_core_news_sm`.
    *   [`Dockerfile.frontend-dev`](Dockerfile.frontend-dev:1) : Structure initiale revue.
    *   [`docker-compose.yml`](docker-compose.yml:1) : Modifié pour définir `VITE_PROXY_API_TARGET_URL` pour le service frontend et suppression de la ligne `version: '3.8'`.
*   Branche Git `dockerisation` créée pour isoler ces travaux.

## Ce qui Reste à Construire / Améliorer (Prochaine Session)

*   **Dockerisation (Priorité Haute - EN COURS, BLOQUÉ) :**
    *   **Résoudre Erreur 404 :** La communication Frontend-Backend sous Docker ne fonctionne pas (les projets ne se chargent pas, erreurs 404 sur les appels API). Nécessite une investigation approfondie des logs, des chemins d'API, de la configuration du proxy Vite et de la résolution DNS inter-conteneurs après un `docker-compose up --build`.
    *   **Valider la correction pour spaCy :** Exécuter `docker-compose up --build` et vérifier les logs backend. Tester les fonctionnalités d'analyse dépendant de spaCy.
    *   **Alternative spaCy :** Si les problèmes avec spaCy persistent (même après correction du Dockerfile), évaluer des bibliothèques alternatives ou discuter de la simplification/suppression des fonctionnalités d'analyse concernées.
    *   Tests fonctionnels complets de l'application une fois les problèmes ci-dessus résolus et l'application fonctionnant sous Docker.
    *   Mise à jour de la documentation [`README.md`](README.md) pour le lancement via Docker et la configuration des clés API.
*   **Commit et Push des changements** de la branche `dockerisation` une fois la Dockerisation fonctionnelle.
*   **Révocation et Remplacement des Clés API Exposées (Action Externe Critique - Rappel).**
*   **(Si temps disponible) Nettoyage des logs de débogage** (style.py, ChapterList.vue).
*   **(Si temps disponible) Bugs des scènes (à réévaluer).**
*   **(Si temps disponible) Exécuter `npm audit fix` et traiter les vulnérabilités.**

## Problèmes Actuels (État Actuel)

*   **Erreur 404 Communication Docker :** Le frontend ne parvient pas à communiquer avec le backend lorsque les deux s'exécutent dans des conteneurs Docker (test utilisateur du 24/05). Les appels API reçoivent des erreurs 404.
*   **Modèle spaCy manquant dans Docker (Correction proposée) :** Les logs du backend (avant la dernière tentative de build refusée) indiquent que le modèle `fr_core_news_sm` (ou `md`) est manquant. Une correction a été ajoutée à [`Dockerfile.backend`](Dockerfile.backend:1) mais n'a pas encore été validée par un build et des tests.
*   Conflit de Dépendance `openai` (Mineur - À surveiller).
*   Scènes Non Fonctionnelles (Reporté - À réévaluer).
*   (Mineur - Reporté) `npm audit`.

## Évolution des Décisions

### Session 24 Mai
*   **Objectif :** Finaliser la Dockerisation.
*   Création de la branche `dockerisation`.
*   Modification de [`frontend/vite.config.js`](frontend/vite.config.js:1) pour rendre la cible du proxy dynamique.
*   Modification de [`docker-compose.yml`](docker-compose.yml:1) pour passer la cible du proxy au conteneur frontend et suppression de la ligne `version`.
*   Refonte des appels API dans tous les composables frontend pour utiliser des chemins relatifs (ex: `/api/projects/`).
*   Identification du problème de modèle spaCy manquant dans les logs Docker du backend.
*   Modification de [`Dockerfile.backend`](Dockerfile.backend:1) pour ajouter le téléchargement du modèle spaCy.
*   **Blocage :** L'utilisateur a testé l'application (probablement avant que les dernières corrections Dockerfile/docker-compose ne soient buildées) et a rencontré des erreurs 404 indiquant un échec de communication frontend-backend sous Docker.
*   **Décision :** Arrêt de la session. Priorité à la mise à jour de la Banque de Mémoire. Le débogage des erreurs 404 et la validation de la correction spaCy sont reportés à la prochaine session. L'utilisateur a suggéré d'envisager une alternative à spaCy si cela s'avère trop bloquant.

### Session 22 Mai - Après-midi (Fin de session)
*   Amélioration Esthétique Dialogue Suppression Clés API : Remplacement de `window.confirm` par `VDialog`. VALIDÉ.
*   Session Terminée. Prochaine priorité (à ce moment) : Dockerisation.
*   Mise à jour de la Banque de Mémoire.

*(Les détails des sessions antérieures au 22 Mai après-midi sont conservés dans activeContext.md)*

*Ce document reflète l'état au 24/05/2025 (07:18).*