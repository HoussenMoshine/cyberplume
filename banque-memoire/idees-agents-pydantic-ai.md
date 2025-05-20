# Idées d'Agents Pydantic AI pour CyberPlume

Ce document recense les idées d'agents IA basés sur `pydantic-ai` qui ont été explorées pour enrichir les fonctionnalités de CyberPlume. Il sert de source d'inspiration pour de futurs développements.

## Contexte

L'exploration de `pydantic-ai` (Session du 13/05/2025) a montré son potentiel pour créer des agents capables de :
- Comprendre des instructions complexes.
- Utiliser des outils pour interagir avec les données de CyberPlume (base de données, contenu des textes).
- Fournir des sorties structurées et validées grâce aux modèles Pydantic.

L'objectif est de développer ces agents de manière modulaire et expérimentale.

## Idées d'Agents Explorées

### 1. Agent "Générateur de Twists Narratifs" (Focus pour prochaine exploration technique)

*   **Concept :** À partir d'un résumé de l'intrigue, d'un chapitre ou d'une scène, l'agent propose plusieurs rebondissements, complications inattendues ou pistes alternatives pour dynamiser le récit.
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class TwistSuggestion(BaseModel):
        title: str = Field(description="Titre court et accrocheur pour le twist.")
        description: str = Field(description="Description détaillée du twist proposé.")
        potential_impact: str = Field(description="Impact potentiel sur l'intrigue, les personnages ou le thème.")
        type: Optional[str] = Field(None, description="Type de twist (ex: révélation, trahison, faux-semblant, dilemme moral).")
        elements_to_introduce: Optional[List[str]] = Field(None, description="Nouveaux éléments (personnages, objets, lieux) que ce twist pourrait nécessiter.")
    
    class NarrativeTwistReport(BaseModel):
        source_summary: str = Field(description="Bref rappel du contexte fourni à l'agent.")
        twist_suggestions: List[TwistSuggestion]
    ```
*   **Outils Potentiels :**
    *   `get_project_summary(project_id: int) -> str`
    *   `get_chapter_summary(chapter_id: int) -> str`
    *   `get_scene_summary(scene_id: int) -> str`
    *   `get_main_characters_info(project_id: int) -> List[dict]`
*   **Modularité & Intégration :**
    *   Pourrait être un service backend distinct.
    *   Accessible via une nouvelle API (ex: `/api/agents/narrative/generate-twists`).
    *   Interface utilisateur : un bouton dans l'éditeur ou le gestionnaire de projet, ouvrant un dialogue pour entrer le contexte et afficher les suggestions.

### 2. Agent "Développeur de Personnage Interactif" (Intérêt marqué)

*   **Concept :** L'agent aide l'utilisateur à approfondir un personnage existant ou à en créer un nouveau par un processus de questions-réponses. L'agent analyse les informations fournies et pose des questions ciblées pour stimuler la réflexion sur la backstory, les motivations, les peurs, les relations, etc.
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional, Dict

    class CharacterInsight(BaseModel):
        aspect: str = Field(description="Aspect du personnage exploré (ex: motivation, peur, relation).")
        generated_idea: str = Field(description="Idée ou développement suggéré par l'agent.")
        follow_up_question: Optional[str] = Field(None, description="Question de l'agent pour approfondir cet aspect.")

    class InteractiveCharacterDevelopmentSession(BaseModel):
        character_id_or_name: str
        session_log: List[Dict[str, str]] # Log des échanges utilisateur/agent
        current_insights_and_suggestions: List[CharacterInsight]
        updated_character_profile_summary: Optional[Dict] = Field(None, description="Résumé du profil personnage mis à jour.")
    ```
*   **Outils Potentiels :**
    *   `get_character_details(character_id_or_name: str) -> dict`
    *   `update_character_field(character_id_or_name: str, field_name: str, new_value: str)`
    *   `get_project_genre_and_themes(project_id: int) -> dict`
*   **Modularité & Intégration :**
    *   Pourrait être un agent conversationnel avec état.
    *   Interface dédiée dans le `CharacterManager`, potentiellement un panneau de chat.

### 3. Agent "Analyseur de Style d'Écriture Comparatif"

*   **Concept :** L'utilisateur fournit deux extraits de texte. L'agent analyse et compare les styles (longueur des phrases, vocabulaire, ton, figures de style, rythme) et fournit un rapport structuré.
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Dict

    class StyleMetrics(BaseModel):
        avg_sentence_length: float
        lexical_diversity: float # (ex: Type-Token Ratio)
        common_keywords: List[str]
        sentiment_analysis: Optional[Dict[str, float]] = None # (ex: {'positive': 0.7, 'neutral': 0.2, 'negative': 0.1})
        dominant_figures_of_style: Optional[List[str]] = None

    class StyleComparisonReport(BaseModel):
        text1_identifier: str
        text2_identifier: str
        text1_analysis: StyleMetrics
        text2_analysis: StyleMetrics
        key_differences: List[str] = Field(description="Points de comparaison saillants.")
        similarity_score: Optional[float] = Field(None, description="Score global de similarité stylistique (0-1).")
    ```
*   **Outils Potentiels :**
    *   Fonctions NLP pour calculer les métriques (longueur de phrase, diversité lexicale). SpaCy pourrait être utilisé ici.
*   **Modularité & Intégration :**
    *   Nouvelle fonctionnalité, potentiellement avec une interface dédiée pour uploader/coller les textes.

### 4. Agent "Créateur de Synopsis Dynamique"

*   **Concept :** Génère ou met à jour un synopsis (logline, points clés de l'intrigue, thèmes) pour un projet ou un chapitre en se basant sur le contenu textuel.
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class Synopsis(BaseModel):
        title: str = Field(description="Titre du projet/chapitre.")
        logline: str = Field(description="Résumé concis en une ou deux phrases.")
        key_plot_points: List[str] = Field(description="Principaux événements ou tournants de l'intrigue.")
        identified_themes: Optional[List[str]] = Field(None, description="Thèmes majeurs qui se dégagent.")
        main_characters_involved: Optional[List[str]] = Field(None, description="Personnages centraux pour ce synopsis.")
    ```
*   **Outils Potentiels :**
    *   `get_full_project_text(project_id: int) -> str`
    *   `get_chapter_text(chapter_id: int) -> str`
    *   `extract_named_entities(text: str) -> List[Dict]`
*   **Modularité & Intégration :**
    *   Pourrait s'intégrer au `ProjectManager` ou être un outil d'analyse accessible via la barre d'outils du projet.

### 5. Agent "Validateur de Lore / Continuité Interne"

*   **Concept :** Spécialisé dans la vérification de la cohérence des règles du monde, des faits établis et de l'historique des personnages. L'utilisateur pourrait "enseigner" le lore à l'agent (par exemple, via des documents dédiés ou une base de connaissances).
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class LoreConflict(BaseModel):
        conflict_description: str = Field(description="Description du conflit de lore détecté.")
        source_of_conflict_1: str = Field(description="Référence au premier élément du lore en conflit (ex: 'Chapitre 3, Scène 2', 'Règle du monde X').")
        source_of_conflict_2: str = Field(description="Référence au second élément du lore en conflit.")
        explanation: Optional[str] = Field(None, description="Explication de la nature du conflit.")
        severity: Optional[str] = Field(None, description="Sévérité estimée (ex: 'mineure', 'majeure', 'critique').")
    
    class LoreValidationReport(BaseModel):
        checked_scope: str # (ex: "Projet entier", "Chapitre 5")
        conflicts_found: List[LoreConflict]
    ```
*   **Outils Potentiels :**
    *   `retrieve_lore_document(topic: str) -> str`
    *   `query_vector_db_lore(query: str) -> List[str]` (si une base vectorielle est utilisée pour le lore)
    *   `get_text_segment(document_name: str, segment_id: str) -> str`
*   **Modularité & Intégration :**
    *   Nécessiterait un système de gestion du "lore".
    *   Pourrait être un agent d'analyse plus avancé.

### 6. Agent "Générateur de Dialogues Contextuels Amélioré"

*   **Concept :** Amélioration de la génération de dialogue existante. L'agent prendrait en compte plus finement la personnalité des personnages (via leurs fiches descriptives), leurs relations, l'historique récent de la conversation dans la scène, et l'objectif émotionnel de la scène.
*   **Sortie Pydantic (Exemple) :**
    ```python
    from pydantic import BaseModel, Field
    from typing import List, Optional

    class DialogueTurn(BaseModel):
        character_name: str
        line_of_dialogue: str
        suggested_tone_or_emotion: Optional[str] = Field(None, description="Ex: 'colérique', 'sarcastique', 'hésitant'.")
        action_or_gesture_hint: Optional[str] = Field(None, description="Ex: 'hausse les épaules', 'regarde par la fenêtre'.")

    class DialogueContinuation(BaseModel):
        scene_context_summary: str
        generated_dialogue_turns: List[DialogueTurn]
    ```
*   **Outils Potentiels :**
    *   `get_character_profile(character_name: str) -> dict`
    *   `get_current_scene_context(scene_id: int) -> dict` (incluant les derniers échanges, personnages présents, objectif de la scène)
*   **Modularité & Intégration :**
    *   Pourrait remplacer ou s'intégrer à la fonction de génération de dialogue existante dans l'[`ActionPanel.vue`](frontend/src/components/ActionPanel.vue:0) ou l'[`ai-toolbar.vue`](frontend/src/components/ai-toolbar.vue:0).