# Plan d'Implémentation : Agent "Générateur de Twists Narratifs"

## Introduction

L'objectif est de rendre l'agent "Générateur de Twists Narratifs" pleinement fonctionnel, de l'appel API backend à l'interaction utilisateur dans le frontend.

Points clés de la conception :
*   L'agent utilisera `pydantic-ai` pour la gestion des outils et la structuration de la sortie.
*   L'agent aura une **configuration LLM (fournisseur, modèle, styles) totalement indépendante**. Son interface utilisateur dédiée comportera ses propres sélecteurs, non pré-remplis par les paramètres IA globaux de l'application.
*   L'implémentation sera modulaire pour ne pas affecter les fonctionnalités IA existantes.

## Phase 1 : Finalisation du Backend

Cette phase se concentre sur la logique métier de l'agent.

```mermaid
graph TD
    subgraph Backend - Agent "Générateur de Twists Narratifs"
        A[Définir le Prompt Système pour l'Agent] --> B(Connecter les Outils à la DB via `crud.py`);
        B --> C(Configurer l'Instance de l'Agent PydanticAI avec Outils & Type de Sortie);
        C --> D(Implémenter Logique Agent dans `narrative_twist_agent.py`);
        D -- Reçoit Fournisseur/Modèle/Style de l'API --> E(Exécuter PydanticAI avec LLM Dynamique à chaque appel `run_sync`);
        E --> F(Finaliser Endpoint API dans `agents.py` pour accepter sélection LLM);
        F --> G(Intégrer Routeur Agent `agents_router` dans `main.py`);
        G --> H(Écrire Tests Unitaires pour Outils, Agent, Endpoint);
    end
```

1.  **Définir un Prompt Système Robuste :**
    *   Créer un prompt système clair et efficace dans [`backend/ai_agents/narrative_twist_agent.py`](backend/ai_agents/narrative_twist_agent.py) pour guider le LLM.
2.  **Connecter les Fonctions Outils à la Base de Données :**
    *   Modifier les fonctions ébauchées dans [`backend/ai_agents/narrative_twist_tools.py`](backend/ai_agents/narrative_twist_tools.py) pour interagir avec la base de données via les fonctions `crud` existantes.
3.  **Configurer l'Instance de l'Agent `PydanticAI` :**
    *   Dans [`backend/ai_agents/narrative_twist_agent.py`](backend/ai_agents/narrative_twist_agent.py), initialiser une instance de `pydantic_ai.Agent`.
    *   Configurer cette instance avec les outils définis (de `narrative_twist_tools.py`) et le type de sortie structurée (par exemple, `NarrativeTwistOutput` depuis [`backend/ai_agents/narrative_twist_models.py`](backend/ai_agents/narrative_twist_models.py)). Le LLM spécifique *ne sera pas* fixé lors de l'initialisation de cet objet `Agent`.
4.  **Implémenter la Logique de l'Agent pour Exécution Dynamique :**
    *   La fonction principale dans [`backend/ai_agents/narrative_twist_agent.py`](backend/ai_agents/narrative_twist_agent.py) (appelée par l'API) recevra en paramètres : le contexte narratif, et les informations sur le fournisseur d'IA, le modèle et les paramètres de style choisis par l'utilisateur.
    *   Cette fonction appellera la méthode `run` (ou `run_sync`) de l'instance `Agent` configurée à l'étape 3, en passant dynamiquement :
        *   Le `model` sous forme de chaîne (ex: `'openai:gpt-4o'`, `'google-gla:gemini-1.5-pro'`).
        *   Les `model_settings` (ex: `{'temperature': 0.7}`) pour appliquer les styles.
5.  **Finaliser l'Endpoint API :**
    *   L'endpoint API dans [`backend/routers/agents.py`](backend/routers/agents.py) devra accepter les paramètres supplémentaires pour le choix du fournisseur, du modèle et du style, en plus du contexte narratif.
    *   Il passera ces paramètres à la logique de l'agent.
6.  **Intégrer le Routeur de l'Agent à l'Application Principale :**
    *   Ajouter `agents_router` (depuis [`backend/routers/agents.py`](backend/routers/agents.py)) à l'application FastAPI principale dans [`backend/main.py`](backend/main.py).
7.  **Écrire des Tests Unitaires :**
    *   Développer des tests unitaires pour les fonctions outils, la logique de l'agent (simulant différents choix de LLM), et l'endpoint API (utilisant le `TestClient` de FastAPI).

## Phase 2 : Développement du Frontend

Cette phase se concentre sur l'interface utilisateur pour interagir avec l'agent.

```mermaid
graph TD
    subgraph Frontend - Interface Agent "Générateur de Twists Narratifs"
        I[Créer Composant/Dialogue UI avec Sélecteurs LLM Indépendants] --> J(Appeler API Backend en transmettant la Sélection LLM/Style);
        J --> K(Afficher Suggestions de Twists de manière conviviale);
        K --> L(Permettre Interaction Utilisateur avec les suggestions);
    end
```

1.  **Créer un Composant/Dialogue UI Dédié :**
    *   Développer un nouveau composant Vue.js (ex: `NarrativeTwistGeneratorDialog.vue` dans `frontend/src/components/dialogs/`).
    *   Ce composant remplacera le placeholder actuel activé par le menu "Agents".
    *   L'interface inclura des contrôles **complets et indépendants** pour la sélection du fournisseur d'IA, du modèle spécifique, et pour l'ajustement des paramètres de style. Ces contrôles ne seront pas liés à l'état de la barre d'outils IA globale.
    *   L'interface permettra à l'utilisateur de fournir le contexte nécessaire (ex: résumé de l'intrigue, personnages).
2.  **Implémenter l'Appel à l'API Backend :**
    *   Dans le nouveau composant UI, utiliser `axios` (via un `composable` existant ou nouveau) pour appeler l'endpoint `/api/agents/narrative/generate-twists`.
    *   Envoyer les données contextuelles et les paramètres de sélection du fournisseur, du modèle et du style.
3.  **Afficher les Suggestions de Twists :**
    *   Présenter les twists narratifs retournés par l'API de manière claire.
4.  **Permettre l'Interaction Utilisateur :**
    *   Fournir des fonctionnalités pour utiliser les suggestions (ex: copier le texte).

## Phase 3 : Tests et Raffinements

1.  **Tests d'Intégration :** Tester le flux complet, du frontend au backend et retour, avec différentes configurations LLM.
2.  **Tests Utilisateur (Simulés) :** Évaluer l'ergonomie de l'interface de l'agent et la pertinence des twists générés.
3.  **Documentation :** Mettre à jour la Banque de Mémoire ([`activeContext.md`](banque-memoire/activeContext.md), [`progress.md`](banque-memoire/progress.md), [`systemPatterns.md`](banque-memoire/systemPatterns.md) si nécessaire) avec les détails de l'implémentation.