# Contexte Actif - CyberPlume (Mise à jour : 21/05/2025 - 09:32)

## Focus Actuel

*   **Fin de session de développement (21 Mai - Matin).**
*   **Résolution du bug OpenRouter :** Confirmé comme résolu par l'utilisateur (clé API révoquée remplacée).
*   **Planification de la fonctionnalité de gestion des clés API utilisateur :** Un plan détaillé a été proposé et discuté.
    *   Décision : Ne pas prioriser HTTPS pour la communication locale frontend-backend pour cette fonctionnalité dans l'immédiat.
*   **Correction du bug d'analyse de contenu de chapitre :** L'erreur "Provider is missing or invalid" lors de l'appel à `triggerChapterAnalysis` depuis [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:296) a été corrigée en passant correctement `props.selectedAiProvider` et `props.selectedAiModel`.
*   Mise à jour de la Banque de Mémoire pour refléter ces points et clore la session.

## Décisions et Actions Clés de la Session (21 Mai - Matin)

*   **Résolution du Bug OpenRouter :**
    *   Confirmé par l'utilisateur que le remplacement de la clé API OpenRouter par une nouvelle clé a résolu l'erreur 401.
*   **Planification de la Gestion des Clés API Utilisateur :**
    *   Un plan détaillé a été élaboré.
    *   Décision de ne pas inclure HTTPS pour la communication locale pour cette fonctionnalité dans l'immédiat.
*   **Correction du Bug d'Analyse de Contenu Chapitre :**
    *   Modification de l'appel à `triggerChapterAnalysis` dans [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:296) pour inclure `props.selectedAiProvider` et `props.selectedAiModel`.
*   **Mise à jour de la Banque de Mémoire.**

## Apprentissages et Patrons Importants Récents (Session 21 Mai - Matin)

*   **Débogage d'Authentification API Externe :** Une clé API invalidée/révoquée est une cause fréquente d'erreur 401.
*   **Révocation Automatique des Clés :** Possible par les fournisseurs en cas de fuite.
*   **Priorisation des Fonctionnalités :** Adapter les plans aux contraintes (ex: HTTPS pour usage local).
*   **Passage de Props aux Composables :** S'assurer que toutes les données nécessaires (comme le fournisseur IA) sont correctement passées des composants aux fonctions des composables.

## Prochaines Étapes (Pour la prochaine session de développement)

1.  **Implémentation de la Fonctionnalité de Configuration des Clés API (Priorité Haute - basée sur le plan détaillé) :**
    *   Développement frontend et backend.
    *   Mise en place du stockage chiffré.
    *   Tests approfondis.
2.  **Reprise et Finalisation de la Dockerisation (après implémentation gestion des clés).**
3.  **Commit et Push des Changements (Rappel - inclure la correction du bug d'analyse de contenu et s'assurer que les changements de sécurité précédents sont poussés).**
4.  **Révocation et Remplacement des Clés API Exposées (Rappel - Action Externe Critique - Vérifier que toutes les clés potentiellement compromises ont été effectivement révoquées et remplacées).**

---
*Historique précédent (avant cette mise à jour) conservé ci-dessous.*
# Contexte Actif - CyberPlume (Mise à jour : 21/05/2025 - 09:18)

## Focus Actuel

*   **Fin de session de développement (21 Mai - Matin).**
*   **Résolution du bug OpenRouter :** Confirmé comme résolu par l'utilisateur (clé API révoquée remplacée).
*   **Planification de la fonctionnalité de gestion des clés API utilisateur :** Un plan détaillé a été proposé et discuté.
    *   Décision : Ne pas prioriser HTTPS pour la communication locale frontend-backend pour cette fonctionnalité dans l'immédiat.
*   Mise à jour de la Banque de Mémoire pour refléter ces points et clore la session de planification.

## Décisions et Actions Clés de la Session (21 Mai - Matin)

*   **Résolution du Bug OpenRouter :**
    *   Confirmé par l'utilisateur que le remplacement de la clé API OpenRouter (qui avait été révoquée, potentiellement automatiquement suite à une fuite) par une nouvelle clé a résolu l'erreur 401.
    *   Le fournisseur OpenRouter est de nouveau opérationnel.
*   **Planification de la Gestion des Clés API Utilisateur :**
    *   Un plan détaillé a été élaboré, couvrant l'UX/UI frontend, la logique backend (endpoints, stockage sécurisé chiffré des clés en base de données), les aspects de sécurité, et l'impact sur la dockerisation.
    *   Il a été décidé de ne pas inclure la mise en place de HTTPS pour la communication locale dans le cadre de cette fonctionnalité pour le moment, tout en gardant cela comme une considération pour un déploiement futur.
*   **Mise à jour de la Banque de Mémoire :** Documentation de la résolution du bug, du plan de gestion des clés API, de la décision concernant HTTPS, et ajustement des priorités.

## Apprentissages et Patrons Importants Récents (Session 21 Mai - Matin)

*   **Débogage d'Authentification API Externe :** Une clé API invalidée ou révoquée côté fournisseur est une cause probable d'erreur 401, surtout si des fuites de secrets ont eu lieu.
*   **Révocation Automatique des Clés :** Les fournisseurs peuvent révoquer les clés compromises.
*   **Priorisation des Fonctionnalités :** Adapter les plans en fonction des contraintes et de l'usage actuel (ex: HTTPS pour usage local).

## Prochaines Étapes (Pour la prochaine session de développement)

1.  **Implémentation de la Fonctionnalité de Configuration des Clés API (Priorité Haute - basée sur le plan détaillé) :**
    *   Développement frontend et backend.
    *   Mise en place du stockage chiffré.
    *   Tests approfondis.
2.  **Reprise et Finalisation de la Dockerisation (après implémentation gestion des clés).**
3.  **Commit et Push des Changements de Sécurité (Rappel - s'assurer que toutes les clés compromises ont été traitées et que les changements liés à la suppression des fichiers de test sont poussés).**
4.  **Révocation et Remplacement des Clés API Exposées (Rappel - Action Externe Critique - Vérifier que toutes les clés potentiellement compromises ont été effectivement révoquées et remplacées).**

---
*Historique précédent (avant cette mise à jour) conservé ci-dessous.*
# Contexte Actif - CyberPlume (Mise à jour : 21/05/2025 - 07:27)

## Focus Actuel

*   **Fin de session de développement (21 Mai - Matin).**
*   Implémentation initiale de la dockerisation (création de `Dockerfile.backend`, `Dockerfile.frontend-dev`, `docker-compose.yml`).
*   Identification d'un obstacle majeur pour la dockerisation en vue de la distribution : la gestion des clés API via les fichiers `.env` n'est pas adaptée.
*   Décision de mettre en pause la finalisation de la dockerisation.
*   Nouvelle priorité : Planifier et implémenter une fonctionnalité permettant aux utilisateurs de configurer leurs clés API directement via l'interface frontend.
*   Mise à jour de la Banque de Mémoire.

## Décisions et Actions Clés de la Session (21 Mai - Matin - Suite)

*   **Implémentation Initiale de la Dockerisation :**
    *   Création du fichier [`Dockerfile.backend`](Dockerfile.backend:1) pour le service FastAPI.
    *   Création du fichier [`Dockerfile.frontend-dev`](Dockerfile.frontend-dev:1) pour le service frontend Vite en mode développement.
    *   Création du fichier [`docker-compose.yml`](docker-compose.yml:1) pour orchestrer les deux services.
    *   Analyse de la configuration CORS et de l'utilisation de `VITE_API_URL` pour la communication inter-conteneurs.

*   **Réorientation Stratégique pour la Gestion des Clés API :**
    *   **Problème identifié :** La dépendance aux fichiers `.env` pour les clés API rend difficile la distribution et le test de l'application par des tiers via Docker.
    *   **Décision :** Mettre en pause les tests et la finalisation de la dockerisation.
    *   **Nouvelle Priorité :** Développer une fonctionnalité permettant aux utilisateurs de saisir et de sauvegarder (localement et de manière sécurisée) leurs clés API pour Gemini, Mistral, et OpenRouter directement depuis une section "Configuration" dans l'interface frontend.

## Apprentissages et Patrons Importants Récents (Session 21 Mai - Matin - Suite)

*   **Distribution d'Applications Dockerisées avec Clés API :** La gestion des secrets et des configurations spécifiques à l'utilisateur est un défi majeur. Les fichiers `.env` locaux ne sont pas une solution portable pour la distribution publique. Des mécanismes de configuration in-app sont souvent nécessaires.
*   **Flexibilité et Réactivité :** Être capable de réévaluer les priorités en fonction des défis rencontrés (comme la gestion des clés API) est crucial pour le développement de projet.

## Prochaines Étapes (Pour la prochaine session de développement)

1.  **Planification Détaillée de la Fonctionnalité de Configuration des Clés API (Priorité Haute) :**
    *   Définir l'UX/UI de la section "Configuration" dans le frontend.
    *   Spécifier comment les clés seront stockées de manière sécurisée (ex: dans la base de données locale SQLite, chiffrées si possible, ou via un mécanisme de stockage sécurisé du système d'exploitation si Electron est utilisé).
    *   Définir les endpoints API backend nécessaires pour recevoir et gérer ces clés.
    *   Adapter la logique backend ([`backend/config.py`](backend/config.py:1), adaptateurs IA) pour utiliser les clés configurées par l'utilisateur en priorité sur celles des fichiers `.env` (qui pourraient servir de fallback ou pour le développement initial).
    *   Documenter ce plan dans la Banque de Mémoire (ex: nouveau fichier `banque-memoire/plan-gestion-cles-api.md`).
2.  **Implémentation de la Fonctionnalité de Configuration des Clés API.**
3.  **Reprise et Finalisation de la Dockerisation :**
    *   Une fois la gestion des clés API via l'interface utilisateur implémentée, reprendre les tests de la configuration Docker.
    *   Mettre à jour la documentation (`README.md`) pour expliquer comment configurer les clés API après avoir lancé l'application via Docker.
4.  **Commit et Push des Changements de Sécurité (Rappel - Priorité Immédiate si pas encore fait) :**
    *   `git add .`
    *   `git commit -m "Fix: Remove test files exposing API keys"` (si ce commit spécifique n'a pas été fait) ou un commit plus large incluant les nouveaux fichiers Docker.
    *   `git push`
5.  **Révocation et Remplacement des Clés API Exposées (Rappel - Action Externe Critique).**

---
*Historique précédent (avant cette mise à jour) conservé ci-dessous.*
# Contexte Actif - CyberPlume (Mise à jour : 21/05/2025 - 06:14)

## Focus Actuel

*   **Début de session de développement (21 Mai - Matin).**
*   Résolution d'un problème de sécurité : Suppression de fichiers de test exposant des clés API.
*   Mise à jour de la Banque de Mémoire.

## Décisions et Actions Clés de la Session (21 Mai - Matin)

*   **Suppression des Fichiers de Test avec Clés API Exposées :**
    *   **Problème :** Les fichiers [`backend/test_gemini.py`](backend/test_gemini.py:1), [`backend/test_mistral.py`](backend/test_mistral.py:1), et [`backend/test_openrouters.py`](backend/test_openrouters.py:1) contenaient des clés API en dur et étaient publiés sur GitHub.
    *   **Analyse :** Une recherche a confirmé que ces fichiers n'étaient pas utilisés par l'application principale.
    *   **Solution :** Suppression des trois fichiers via la commande `rm backend/test_gemini.py backend/test_mistral.py backend/test_openrouters.py`.
    *   **Résultat :** Les fichiers exposant les clés API ont été supprimés du projet. Il est crucial de s'assurer que ces changements sont committés et poussés sur GitHub, et que les clés API concernées sont révoquées et remplacées si nécessaire.

## Apprentissages et Patrons Importants Récents (Session 21 Mai - Matin)

*   **Sécurité des Clés API :** Ne jamais commiter de clés API ou d'autres informations sensibles directement dans le code source, surtout pour les dépôts publics. Utiliser des variables d'environnement et des fichiers `.gitignore` de manière appropriée.
*   **Nettoyage Régulier :** Examiner et supprimer régulièrement les fichiers de test ou de brouillon qui ne sont plus nécessaires, en particulier s'ils pourraient contenir des informations sensibles ou obsolètes.

## Prochaines Étapes (Pour cette session de développement ou la suivante)

1.  **Commit et Push des Changements de Sécurité (Priorité Immédiate) :**
    *   `git add .`
    *   `git commit -m "Fix: Remove test files exposing API keys"`
    *   `git push`
2.  **Révocation et Remplacement des Clés API (Action Externe Critique) :** L'utilisateur doit être informé de révoquer les clés API qui ont été exposées (`AIzaSyBAHyupnFpV1iyZo4IiniJGyklnEU1-Z_E`, `CXaga1oCfRdswb9jJ8ya7efuqVv4h4Lq`, `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`) auprès des fournisseurs respectifs (Google, Mistral, OpenRouter) et de les remplacer par de nouvelles clés dans la configuration d'environnement sécurisée ([`backend/.env`](backend/.env:1)).
3.  **Implémentation de la Dockerisation (Priorité Haute - Reprise de la session précédente) :**
    *   Créer le fichier `Dockerfile.backend` pour le service FastAPI.
    *   Créer le fichier `Dockerfile.frontend-dev` pour le service frontend Vite en mode développement.
    *   Créer et configurer le fichier `docker-compose.yml` pour orchestrer les deux services, y compris les volumes pour le code source (hot-reloading) et la base de données, ainsi que la gestion des variables d'environnement.
    *   Tester la configuration Docker en lançant `docker-compose up`.
    *   (Optionnel) Nettoyer les logs de débogage ajoutés dans [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:1) si ce n'est pas déjà fait.
4.  **Tests Post-Publication GitHub (à confirmer si faits en détail par l'utilisateur) :**
    *   Cloner le dépôt dans un nouvel environnement.
    *   Suivre scrupuleusement les instructions du [`README.md`](README.md:1) pour tester l'installation et le lancement.
    *   Vérifier la compatibilité des tests backend après la mise à jour de `httpx`.
5.  **Aborder les autres problèmes en attente (si le temps le permet) :**
    *   Nettoyage des logs de débogage dans [`backend/routers/style.py`](backend/routers/style.py:1).
    *   Bugs des scènes (à réévaluer).
    *   `npm audit`.
    *   Conflit de dépendance `openai` (à vérifier si toujours pertinent).

---
*Historique précédent (avant cette mise à jour) conservé ci-dessous.*
# Contexte Actif - CyberPlume (Mise à jour : 20/05/2025 - 14:32)

## Focus Actuel

*   **Fin de session de développement (20 Mai - Fin d'après-midi).**
*   Correction de bugs liés à la gestion des chapitres (ajout, renommage).
*   Mise à jour de la Banque de Mémoire.

## Décisions et Actions Clés de la Session (20 Mai - Fin d'après-midi - Suite)

*   **Correction du Bug d'Ajout de Chapitre :**
    *   **Problème :** L'ajout de nouveaux chapitres ne fonctionnait pas. L'appel à la fonction `addChapter` dans le composable `useChapters.js` depuis [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:338) était incorrect. Il passait un objet unique `newChapterData` au lieu des arguments `projectId` et `title` attendus séparément.
    *   **Solution :** Modification de la fonction `handleAddChapterDialogSave` dans [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:331) pour appeler `addChapter(props.projectId, title)`.
    *   **Résultat :** L'ajout de chapitres est de nouveau fonctionnel.

*   **Correction du Bug de Renommage de Chapitre (Rafraîchissement UI) :**
    *   **Problème :** Après avoir renommé un chapitre, l'interface utilisateur ne se mettait pas à jour immédiatement (nécessitant un rechargement de page) et une erreur `TypeError: Cannot destructure property 'projectId' of 'undefined'` apparaissait dans la console. L'événement `chapter-updated` était émis par [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:373) sans les données nécessaires (`projectId`, `chapterId`).
    *   **Solution :** Modification de la fonction `submitEditChapter` dans [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:363) pour que l'émission de l'événement `chapter-updated` inclue un objet `{ projectId: props.projectId, chapterId: editingChapter.value.id }`.
    *   **Résultat :** Le renommage des chapitres se reflète maintenant correctement et immédiatement dans l'interface, et l'erreur console est résolue.

## Apprentissages et Patrons Importants Récents (Session 20 Mai - Fin d'après-midi - Suite)

*   **Signature des Fonctions Composables :** Une attention continue est nécessaire pour s'assurer que les appels aux fonctions (surtout celles des composables Vue) respectent scrupuleusement la signature attendue (nombre, ordre et type des arguments).
*   **Payload des Événements Vue (`$emit`) :** Lors de l'émission d'événements entre composants, il est crucial que le payload émis corresponde à ce que le composant parent attend, surtout si le parent déstructure l'argument reçu. Un payload manquant ou mal formé conduit à des erreurs `undefined`.

## Prochaines Étapes (Pour la prochaine session de développement)

1.  **Implémentation de la Dockerisation (Priorité Haute) :**
    *   Créer le fichier `Dockerfile.backend` pour le service FastAPI.
    *   Créer le fichier `Dockerfile.frontend-dev` pour le service frontend Vite en mode développement.
    *   Créer et configurer le fichier `docker-compose.yml` pour orchestrer les deux services, y compris les volumes pour le code source (hot-reloading) et la base de données, ainsi que la gestion des variables d'environnement.
    *   Tester la configuration Docker en lançant `docker-compose up`.
    *   (Optionnel) Nettoyer les logs de débogage ajoutés dans [`frontend/src/components/ChapterList.vue`](frontend/src/components/ChapterList.vue:1) si ce n'est pas déjà fait.
2.  **Tests Post-Publication GitHub (à confirmer si faits en détail par l'utilisateur) :**
    *   Cloner le dépôt dans un nouvel environnement.
    *   Suivre scrupuleusement les instructions du [`README.md`](README.md:1) pour tester l'installation et le lancement.
    *   Vérifier la compatibilité des tests backend après la mise à jour de `httpx`.
3.  **Aborder les autres problèmes en attente (si le temps le permet) :**
    *   Nettoyage des logs de débogage dans [`backend/routers/style.py`](backend/routers/style.py:1).
    *   Bugs des scènes (à réévaluer).
    *   `npm audit`.
    *   Conflit de dépendance `openai` (à vérifier si toujours pertinent).

---
*Historique précédent (avant le 20/05/2025 - Après-midi) conservé ci-dessous.*
# Contexte Actif - CyberPlume (Mise à jour : 20/05/2025 - 13:42)

## Focus Actuel

*   **Fin de session de développement (20 Mai - Après-midi).**
*   Initialisation Git et publication du projet sur GitHub.
*   Améliorations du fichier `README.md`.
*   Mise à jour de la Banque de Mémoire.
*   Planification de la dockerisation pour la prochaine session.

## Décisions et Actions Clés de la Session (20 Mai - Après-midi)