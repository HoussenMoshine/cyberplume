# Intégration d'Agents IA dans CyberPlume avec Pydantic AI

Ce document explore comment l'intégration d'agents IA, facilitée par la bibliothèque `pydantic-ai`, pourrait améliorer et étendre les fonctionnalités de CyberPlume.

## 1. Introduction : Agents IA et Pydantic AI

### Qu'est-ce qu'un Agent IA ?

Un agent IA, dans ce contexte, est un système qui utilise un modèle de langage large (LLM) comme "cerveau" pour raisonner, planifier et exécuter des tâches. Contrairement à un simple appel LLM qui prend une entrée et retourne une sortie textuelle, un agent peut :

*   **Utiliser des Outils :** Exécuter des fonctions prédéfinies (ex: rechercher dans la base de données, appeler une API externe) pour obtenir des informations ou effectuer des actions.
*   **Raisonner en Plusieurs Étapes :** Décomposer une tâche complexe en sous-tâches et décider de la séquence d'actions (appels LLM, utilisation d'outils) nécessaire pour atteindre l'objectif.
*   **Produire une Sortie Structurée :** Générer des résultats dans un format spécifique et validé, souvent basé sur des modèles de données (comme les modèles Pydantic).

### Pourquoi Pydantic AI ?

`pydantic-ai` est un framework qui simplifie la création d'agents IA en Python. Ses avantages clés sont :

*   **Intégration Pydantic :** Permet de définir facilement la structure de sortie attendue de l'agent en utilisant des modèles Pydantic. L'agent force le LLM à générer une sortie conforme à ce modèle.
*   **Support Multi-Provider :** Intègre nativement ou via des adaptateurs compatibles OpenAI de nombreux fournisseurs de LLM (Gemini, Mistral, OpenAI, Cohere, Anthropic via Bedrock/OpenRouter, Ollama local, etc.), s'alignant bien avec l'architecture actuelle de CyberPlume.
*   **Gestion des Outils (Tools) :** Fournit un mécanisme simple pour définir et exposer des fonctions Python comme outils utilisables par l'agent.
*   **Framework Agentique :** Offre la classe `Agent` qui orchestre les interactions entre le LLM, les outils et la gestion de la sortie structurée.

## 2. Concepts Clés de Pydantic AI

*   **`Agent` :** La classe principale. On l'initialise avec un modèle LLM et potentiellement un `output_type` (un modèle Pydantic).
    ```python
    from pydantic_ai import Agent
    from pydantic import BaseModel

    class MyOutput(BaseModel):
        result: str
        confidence: float

    # Initialisation simple (le provider est déduit ou utilise les variables d'env)
    agent = Agent('google-gla:gemini-2.0-flash', output_type=MyOutput)
    ```
*   **`Model` / `Provider` :** Permettent de configurer précisément le LLM à utiliser, y compris les endpoints spécifiques (pour OpenRouter, Together AI, Ollama local, etc.) et les clés API.
    ```python
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider

    # Exemple avec Ollama local
    ollama_model = OpenAIModel(
        model_name='llama3.2', # Nom du modèle servi par Ollama
        provider=OpenAIProvider(base_url='http://localhost:11434/v1') # Endpoint local Ollama
    )
    agent = Agent(ollama_model, output_type=MyOutput)
    ```
*   **`output_type` :** Un modèle Pydantic qui définit la structure de la réponse attendue de l'agent. `pydantic-ai` guide le LLM pour générer une sortie JSON conforme à ce modèle.
*   **`Tools` (Outils) :** Des fonctions Python décorées ou simplement passées à l'agent, que le LLM peut décider d'appeler pour accomplir sa tâche.
    ```python
    from pydantic import Field

    def get_word_count(text: str) -> int:
        """Calculates the word count of the given text."""
        return len(text.split())

    # L'agent peut utiliser cet outil si on le lui fournit
    agent_with_tool = Agent(
        'google-gla:gemini-2.0-flash',
        tools=[get_word_count]
    )
    # Exemple d'appel qui pourrait utiliser l'outil
    # result = await agent_with_tool.run("Summarize the following text and tell me its word count: ...")
    ```

## 3. Cas d'Usage Potentiels dans CyberPlume

L'approche par agent ouvre des possibilités pour des fonctionnalités IA plus sophistiquées et fiables dans CyberPlume.

### a. Agent "Analyseur de Cohérence Narrative"

*   **Objectif :** Aller au-delà de la simple extraction d'entités (actuellement faite avec spaCy) pour activement rechercher et signaler des incohérences potentielles dans un projet ou un chapitre.
*   **Modèle Pydantic de Sortie :**
    ```python
    class InconsistencyWarning(BaseModel):
        type: str = Field(description="Type d'incohérence (ex: 'timeline', 'character_presence', 'contradiction', 'plot_hole')")
        description: str = Field(description="Description détaillée de l'incohérence détectée.")
        location_hint: Optional[str] = Field(None, description="Indice sur l'emplacement (ex: 'Chapitre 5 vs Chapitre 12', 'Scène X')")
        severity: Optional[str] = Field(None, description="Sévérité estimée (ex: 'mineure', 'majeure')")

    class InconsistencyReport(BaseModel):
        warnings: List[InconsistencyWarning]
    ```
*   **Outils Potentiels :**
    *   `get_chapter_content(chapter_id: int) -> str`: Récupère le texte d'un chapitre.
    *   `get_scene_content(scene_id: int) -> str`: Récupère le texte d'une scène.
    *   `get_project_summary(project_id: int) -> str`: Récupère un résumé ou synopsis du projet.
    *   `get_character_mentions(project_id: int, character_name: str) -> List[str]`: Liste les chapitres/scènes où un personnage est mentionné.
    *   `get_timeline_events(project_id: int) -> List[Dict]`: Extrait les événements datés ou ordonnés.
*   **Fonctionnement :** L'agent recevrait l'ID du projet/chapitre. Il utiliserait les outils pour collecter les informations pertinentes (textes, mentions, événements), puis demanderait au LLM d'analyser ces informations pour détecter les incohérences et de formater le résultat selon `InconsistencyReport`.

### b. Agent "Développeur de Personnage"

*   **Objectif :** Aider l'utilisateur à étoffer un personnage en générant des idées de backstory, traits de caractère, motivations, ou relations, en cohérence avec le projet existant.
*   **Modèle Pydantic de Sortie :**
    ```python
    class CharacterDevelopmentIdeas(BaseModel):
        suggested_backstory_elements: Optional[List[str]] = None
        suggested_traits: Optional[List[str]] = None
        suggested_motivations: Optional[List[str]] = None
        suggested_relationships: Optional[List[Dict[str, str]]] = Field(None, description="Liste de dict {'character_name': 'relation_type'}")
    ```
*   **Outils Potentiels :**
    *   `get_character_info(character_id: int) -> Dict`: Récupère les détails actuels du personnage (nom, description, backstory existante).
    *   `get_project_context(project_id: int) -> Dict`: Récupère le genre, le ton, le synopsis du projet.
    *   `get_character_scenes(character_id: int) -> List[Dict]`: Récupère les scènes où le personnage apparaît et potentiellement un résumé de ses actions.
*   **Fonctionnement :** L'agent prendrait l'ID du personnage et potentiellement un objectif spécifique (ex: "générer une backstory tragique"). Il utiliserait les outils pour comprendre le personnage et le contexte du projet, puis demanderait au LLM de générer des idées structurées selon `CharacterDevelopmentIdeas`.

### c. Agent "Générateur de Scène Structuré"

*   **Objectif :** Générer une ébauche de scène plus utilisable qu'un simple bloc de texte, en structurant la description, les actions et les dialogues.
*   **Modèle Pydantic de Sortie :**
    ```python
    class SceneDraft(BaseModel):
        suggested_title: Optional[str] = None
        setting_description: str = Field(description="Description de l'environnement, ambiance.")
        character_actions: List[str] = Field(description="Liste décrivant les actions clés des personnages.")
        dialogue_snippets: List[Dict[str, str]] = Field(description="Liste de dict {'character': 'line'}")
        narrative_summary: Optional[str] = Field(None, description="Très court résumé de l'objectif ou de l'avancement de l'intrigue dans la scène.")
    ```
*   **Outils Potentiels :**
    *   `get_character_info(character_name: str) -> Dict`: Récupère les infos d'un personnage par son nom.
    *   `get_previous_scene_summary(current_chapter_id: int, current_scene_order: int) -> str`: Résumé de la scène précédente.
*   **Fonctionnement :** L'agent recevrait une description de l'objectif de la scène, les personnages présents, l'ambiance souhaitée. Il utiliserait les outils pour obtenir des détails sur les personnages et le contexte, puis demanderait au LLM de générer la scène structurée selon `SceneDraft`.

### d. Agent "Correcteur/Améliorateur de Texte" (Alternative)

*   **Objectif :** Remplacer l'approche actuelle de l'API `/analyze-content` par un agent qui retourne directement les suggestions structurées. L'avantage principal serait la robustesse du formatage de sortie grâce à `output_type`.
*   **Modèle Pydantic de Sortie :** (Similaire à ce qui a été implémenté)
    ```python
    class CorrectionSuggestion(BaseModel):
        original_text: str
        suggested_text: str
        suggestion_type: str
        explanation: Optional[str] = None
        start_index: int
        end_index: int

    class TextAnalysisResult(BaseModel):
        suggestions: List[CorrectionSuggestion]
    ```
*   **Outils Potentiels :** Généralement aucun outil externe nécessaire pour cette tâche spécifique.
*   **Fonctionnement :** L'agent recevrait le texte du chapitre et serait configuré avec `output_type=TextAnalysisResult`. Le prompt demanderait les corrections et améliorations en respectant le format JSON attendu.

## 4. Intégration Technique dans CyberPlume (Backend FastAPI)

1.  **Dépendance :** Ajouter `pydantic-ai` (et potentiellement `pydantic-ai[logfire]` pour le logging) au fichier `backend/requirements.txt` et installer.
2.  **Nouveau Module :** Créer un répertoire `backend/agents/`.
3.  **Modèles Pydantic :** Définir les modèles Pydantic pour les `output_type` des agents (ex: `InconsistencyReport`, `CharacterDevelopmentIdeas`, etc.) dans `backend/agents/schemas.py`.
4.  **Outils :** Implémenter les fonctions Python qui serviront d'outils dans `backend/agents/tools.py`. Ces fonctions interagiront probablement avec la base de données (via des fonctions CRUD existantes ou nouvelles) pour récupérer les informations nécessaires.
    ```python
    # Exemple dans backend/agents/tools.py
    from ..database import SessionLocal
    from .. import models # Accès aux modèles SQLAlchemy

    def get_character_info(character_id: int) -> dict:
        """Retrieves basic information for a given character ID."""
        db = SessionLocal()
        try:
            character = db.query(models.Character).filter(models.Character.id == character_id).first()
            if character:
                return {"name": character.name, "description": character.description, "backstory": character.backstory}
            else:
                return {"error": "Character not found"}
        finally:
            db.close()
    ```
5.  **Implémentation des Agents :** Créer les classes d'agents dans des fichiers dédiés (ex: `backend/agents/consistency_agent.py`, `backend/agents/character_agent.py`).
    ```python
    # Exemple dans backend/agents/character_agent.py
    from pydantic_ai import Agent
    from .schemas import CharacterDevelopmentIdeas
    from .tools import get_character_info, get_project_context # etc.
    from ..ai_services.factory import create_adapter # Utiliser notre factory existante
    from ..config import settings

    def get_character_developer_agent(provider: str, model: Optional[str] = None) -> Agent:
        api_key = getattr(settings, f"{provider}_api_key", None)
        if not api_key:
            raise ValueError(f"API key for provider {provider} not configured.")

        llm = create_adapter(provider, api_key=api_key, model=model) # Réutilise notre logique

        character_agent = Agent(
            llm,
            output_type=CharacterDevelopmentIdeas,
            tools=[get_character_info, get_project_context],
            system_prompt="You are an AI assistant helping a writer develop characters..."
            # Ajouter d'autres configurations si nécessaire
        )
        return character_agent
    ```
6.  **Nouvelles Routes API :** Créer un nouveau routeur FastAPI (ex: `backend/routers/agents.py`) pour exposer les fonctionnalités des agents.
    ```python
    # Exemple dans backend/routers/agents.py
    from fastapi import APIRouter, HTTPException, Depends
    from ..agents.character_agent import get_character_developer_agent
    from ..agents.schemas import CharacterDevelopmentIdeas # Le schéma de sortie

    router = APIRouter(prefix="/api/agents", tags=["agents"])

    class DevelopCharacterRequest(BaseModel):
        provider: str
        model: Optional[str] = None
        objective: Optional[str] = None # Ex: "Generate backstory ideas"

    @router.post("/characters/{character_id}/develop", response_model=CharacterDevelopmentIdeas)
    async def develop_character_agent(character_id: int, request: DevelopCharacterRequest):
        try:
            agent = get_character_developer_agent(request.provider, request.model)
            # Construire le prompt pour l'agent basé sur character_id et request.objective
            prompt = f"Develop character with ID {character_id}. Objective: {request.objective or 'General development ideas'}."
            result = await agent.run(prompt)
            return result.output # Retourne l'objet CharacterDevelopmentIdeas validé
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Log l'erreur complète
            raise HTTPException(status_code=500, detail="Agent execution failed.")
    ```
7.  **Configuration :** S'assurer que les clés API et les modèles par défaut sont bien gérés dans `backend/config.py` et le fichier `.env`.

## 5. Conclusion

L'utilisation de `pydantic-ai` offre une voie prometteuse pour intégrer des fonctionnalités IA plus complexes et structurées dans CyberPlume. En définissant clairement les objectifs, les outils nécessaires et les formats de sortie attendus (via Pydantic), on peut créer des agents spécialisés pour l'analyse de cohérence, le développement de personnages, la génération de scènes, etc.

**Avantages :**
*   **Sortie Structurée et Fiable :** Réduit les problèmes de parsing de texte libre retourné par les LLMs.
*   **Extensibilité :** Facilite l'ajout de nouvelles capacités en définissant de nouveaux outils (fonctions Python).
*   **Raisonnement :** Permet au LLM de choisir les bons outils et d'enchaîner les étapes pour des tâches complexes.
*   **Code Organisé :** Sépare la logique de l'agent, ses outils et ses schémas de sortie.

**Défis :**
*   **Conception des Prompts :** Rédiger des prompts efficaces qui guident l'agent et l'utilisation des outils est crucial.
*   **Gestion des Outils :** Définir les bons outils avec des descriptions claires pour que le LLM sache quand les utiliser.
*   **Complexité :** L'ajout d'agents augmente la complexité globale de l'application.
*   **Coût et Latence :** Les agents peuvent nécessiter plusieurs appels LLM et appels d'outils, augmentant le coût et le temps de réponse.

L'intégration pourrait se faire progressivement, en commençant par un cas d'usage simple comme l'agent correcteur ou l'agent développeur de personnage, avant de s'attaquer à des tâches plus complexes comme l'analyse de cohérence narrative complète.