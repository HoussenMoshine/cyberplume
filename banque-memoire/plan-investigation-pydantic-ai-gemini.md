# Plan d'Investigation et de Résolution - Pydantic-AI & Gemini

**Objectif principal :** Comprendre comment utiliser `pydantic-ai` avec Gemini pour la sortie structurée en se basant sur les exemples officiels, afin de résoudre l'erreur `GenerateContentRequest.contents: contents is not specified`.

**Date de création :** 15/05/2025

## 1. Phase 1: Exploration des Exemples et de la Documentation `pydantic-ai` locaux (Terminée)
    *   **Action 1.1 :** Lister le contenu des répertoires d'exemples (`/mnt/serveur/serveur/test/pydantic-ai/examples`) et de documentation (`/mnt/serveur/serveur/test/pydantic-ai/docs`). (Fait)
    *   **Action 1.2 :** Lire les exemples pertinents, notamment [`pydantic_model.py`](/mnt/serveur/serveur/test/pydantic-ai/examples/pydantic_ai_examples/pydantic_model.py). (Fait)
    *   **Action 1.3 :** Consulter la documentation pertinente, notamment [`docs/models/gemini.md`](/mnt/serveur/serveur/test/pydantic-ai/docs/models/gemini.md) et [`docs/examples/index.md`](/mnt/serveur/serveur/test/pydantic-ai/docs/examples/index.md). (Fait)

## 2. Phase 2: Comparaison et Analyse Différentielle (En cours)
    *   **Action 2.1 : Comparer l'exemple fonctionnel ([`pydantic_model.py`](/mnt/serveur/serveur/test/pydantic-ai/examples/pydantic_ai_examples/pydantic_model.py)) avec le script de test minimal ([`backend/tests/test_pydantic_ai_gemini_minimal.py`](backend/tests/test_pydantic_ai_gemini_minimal.py)).**
        *   Différence clé identifiée : L'exemple utilise `agent.run_sync()` tandis que le script de test minimal et l'agent `NarrativeTwistAgent` utilisent une approche asynchrone (`await agent.run()` ou implicitement via une méthode `async`).
    *   **Action 2.2 : Formuler des hypothèses.**
        *   Hypothèse principale : L'erreur `GenerateContentRequest.contents: contents is not specified` avec Gemini (via l'API Generative Language) et `pydantic-ai` (v0.2.3) est potentiellement liée à la gestion des requêtes *asynchrones* lorsque une sortie structurée (modèle Pydantic) est demandée.

## 3. Phase 3: Proposition de Correctifs et Validation (À venir)
    *   **Action 3.1 : Modifier et exécuter le script de test minimal ([`backend/tests/test_pydantic_ai_gemini_minimal.py`](backend/tests/test_pydantic_ai_gemini_minimal.py)) pour utiliser `agent.run_sync()`.**
        *   Objectif : Vérifier si l'exécution synchrone résout l'erreur `contents is not specified`.
    *   **Action 3.2 : Si `run_sync()` fonctionne dans le script minimal, analyser les implications pour `NarrativeTwistAgent`.**
        *   Si l'agent `NarrativeTwistAgent` doit impérativement rester asynchrone (ce qui est probable dans un contexte FastAPI), il faudra envisager des stratégies pour exécuter la partie `pydantic-ai` de manière synchrone dans un contexte asynchrone (par exemple, avec `asyncio.to_thread` si la version de Python le permet, ou en investiguant plus profondément le code source asynchrone de `pydantic-ai` pour Gemini).
        *   Si `run_sync()` ne résout pas le problème dans le script minimal, d'autres pistes devront être explorées (ex: vérifier la version de la bibliothèque `google-generativeai` utilisée par `pydantic-ai` par rapport à celle potentiellement utilisée par les exemples, examiner la structure exacte du prompt interne que `pydantic-ai` construit pour Gemini).
    *   **Action 3.3 : Planifier l'application des correctifs (ou de la solution de contournement) à l'agent `NarrativeTwistAgent` une fois la cause racine identifiée et une solution validée.**

## 4. Phase 4: Documentation et Prochaines Étapes (À venir)
    *   **Action 4.1 :** Documenter les découvertes, les tests effectués, et la solution (ou les raisons de l'échec) dans la Banque de Mémoire (principalement `activeContext.md` et `progress.md`).
    *   **Action 4.2 :** Définir les prochaines étapes claires pour l'implémentation complète de la solution dans `NarrativeTwistAgent` et la reprise des tests des autres fournisseurs (OpenRouter, Mistral).

## Diagramme Mermaid du Plan

```mermaid
graph TD
    A[Début de la Tâche] --> B{Phase 1: Exploration Locale pydantic-ai};
    B -- Terminé --> B1[1.1: Lister exemples/docs];
    B1 -- Terminé --> B2[1.2: Lire pydantic_model.py];
    B2 -- Terminé --> B3[1.3: Consulter docs Gemini & Exemples Index];

    B3 --> C{Phase 2: Comparaison & Analyse};
    C --> C1[2.1: Comparer pydantic_model.py vs test_minimal.py];
    C1 --> C2[2.2: Hypothèse: Problème avec async pour Gemini];

    C2 --> D{Phase 3: Correctifs & Validation};
    D --> D1[3.1: Modifier test_minimal.py pour utiliser run_sync];
    D1 --> D2[3.2: Analyser implications pour NarrativeTwistAgent si run_sync OK];
    D2 --> D3[3.3: Planifier modifs pour NarrativeTwistAgent];

    D3 --> E{Phase 4: Documentation & Suite};
    E --> E1[4.1: Mettre à jour Banque de Mémoire];
    E1 --> E2[4.2: Définir prochaines étapes d'implémentation];
    E2 --> F[Fin de la Planification];