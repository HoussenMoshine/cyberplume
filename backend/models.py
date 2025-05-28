from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column # Ajout Mapped, mapped_column pour syntaxe moderne optionnelle
from sqlalchemy.sql import func # Pour default=func.now() si besoin
from pydantic import BaseModel, Field # Ajout Field
from typing import List, Optional # Assurer que List est importé

# Importer Base depuis database.py
from .database import Base

# --- Forward declaration pour les types dans les schémas ---
# Nécessaire car SceneRead utilise CharacterRead et vice-versa (potentiellement)
class CharacterRead(BaseModel): # Forward declaration
    id: int # Ajout d'un champ minimal pour que Pydantic ne se plaigne pas trop tôt
    name: str
    # scenes: List['SceneRead'] = [] # Commenté pour éviter une dépendance circulaire trop complexe au stade de la forward declaration

    class Config:
        from_attributes = True

class SceneRead(BaseModel): # Forward declaration
    id: int # Ajout d'un champ minimal
    title: str
    # characters: List[CharacterRead] = [] # Commenté pour la même raison

    class Config:
        from_attributes = True


# --- Schémas Pydantic pour la création ---

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ChapterBase(BaseModel):
    title: str
    content: Optional[str] = None
    pov_character_id: Optional[int] = None
    order: Optional[int] = None # NOUVEAU: Ordre du chapitre dans le projet
    summary: Optional[str] = None # NOUVEAU: Résumé du chapitre

class ChapterCreate(ChapterBase):
    project_id: int

class ChapterCreateNoProjectId(ChapterBase):
    pass

# NOUVEAU: Schémas Pydantic pour Scene
class SceneBase(BaseModel):
    title: str
    content: Optional[str] = None
    order: Optional[int] = None # Ordre de la scène dans le chapitre

class SceneCreate(SceneBase):
    # chapter_id sera fourni par l'URL ou le contexte
    pass

# --- Schémas Pydantic pour la mise à jour ---

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    pov_character_id: Optional[int] = None
    order: Optional[int] = None # NOUVEAU: Permettre la mise à jour de l'ordre
    summary: Optional[str] = None # NOUVEAU: Permettre la mise à jour du résumé

# NOUVEAU: Schéma Pydantic pour Scene Update
class SceneUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    # On ne met pas à jour les personnages liés directement ici,
    # on utilisera des endpoints dédiés /scenes/{id}/characters/{char_id} (POST/DELETE)

# --- Schémas Pydantic pour les Personnages ---

class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    backstory: Optional[str] = None

class CharacterCreate(CharacterBase):
    pass

# MODIFICATION: CharacterRead inclut maintenant les IDs des scènes liées
# Mise à jour de la forward declaration pour CharacterRead
CharacterRead.model_fields.update(SceneRead.model_fields) # Simule une mise à jour, Pydantic gère mieux avec `model_rebuild`

class CharacterRead(CharacterBase): # Redéfinition complète après que SceneRead soit connu (ou du moins sa forward declaration)
    id: int
    scenes: List[SceneRead] = [] 

    class Config:
        from_attributes = True

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    backstory: Optional[str] = None

# --- Schémas Pydantic pour les Clés API (NOUVEAU) ---

class ApiKeyBase(BaseModel):
    provider_name: str = Field(..., description="Nom du fournisseur (ex: gemini, mistral, openrouter)")

class ApiKeyCreate(ApiKeyBase):
    api_key: str = Field(..., description="Clé API en clair")

class ApiKeyUpdate(BaseModel): # Peut être utilisé pour mettre à jour la clé d'un fournisseur existant
    api_key: str = Field(..., description="Nouvelle clé API en clair")

class ApiKeyRead(ApiKeyBase):
    id: int
    has_key_set: bool = Field(..., description="Indique si une clé est configurée pour ce fournisseur")

    class Config:
        from_attributes = True

# --- Schémas Pydantic pour la lecture (Réponses API) ---

# MODIFICATION: SceneRead inclut maintenant les personnages liés
# Mise à jour de la forward declaration pour SceneRead
SceneRead.model_fields.update(CharacterRead.model_fields) # Simule une mise à jour

class SceneRead(SceneBase): # Redéfinition complète
    id: int
    chapter_id: int
    characters: List[CharacterRead] = [] 

    class Config:
        from_attributes = True


class ChapterReadBasic(BaseModel): # Utilisé dans ProjectRead
    id: int
    title: str
    project_id: int
    order: int # NOUVEAU: Inclure l'ordre
    scenes: List[SceneRead] = [] # Ajouté pour afficher les scènes dans la liste des chapitres

    class Config:
        from_attributes = True

class ProjectRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    chapters: List[ChapterReadBasic] = [] # Doit être trié par 'order' par l'API

    class Config:
        from_attributes = True

class ChapterRead(BaseModel): # Pour lire un chapitre complet
    id: int
    title: str
    content: Optional[str] = None
    project_id: int
    pov_character_id: Optional[int] = None
    order: int # NOUVEAU: Inclure l'ordre
    summary: Optional[str] = None # NOUVEAU: Inclure le résumé
    scenes: List[SceneRead] = [] # Inclure les scènes lors de la lecture d'un chapitre (déjà triées par Scene.order)

    class Config:
        from_attributes = True


# --- Schémas pour la génération de personnage ---

class CharacterGenerateRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    style: Optional[str] = None
    prompt_details: Optional[str] = None
    # Champs optionnels pour les caractéristiques
    ethnicity: Optional[str] = None
    gender: Optional[str] = None
    approx_age: Optional[str] = None
    nationality: Optional[str] = None
    job: Optional[str] = None # NOUVEAU
    clothing: Optional[str] = None # NOUVEAU

class CharacterGenerateResponse(BaseModel):
    name: str
    description: Optional[str] = None
    backstory: Optional[str] = None
    raw_response: str

# --- Schémas pour la génération de scène ---

class SceneGenerateRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    style: Optional[str] = None
    prompt_details: Optional[str] = None
    chapter_context: Optional[str] = None

class SceneGenerateResponse(BaseModel):
    generated_text: str
    raw_response: str

# --- Schémas Pydantic pour la suppression multiple ---

class DeleteBatchSchema(BaseModel):
    ids: List[int]

# --- NOUVEAU: Schéma pour le réordonnancement ---
class ReorderItemsSchema(BaseModel):
    ordered_ids: List[int]

# --- Schémas pour l'analyse ---
class StyleAnalysisRequest(BaseModel):
    text_to_analyze: str
    # Ajoutez d'autres champs si nécessaire (ex: style de référence)

class StyleAnalysisResponse(BaseModel):
    analysis_id: str # Un identifiant pour cette analyse
    # Ajoutez les résultats de l'analyse de style ici
    # Par exemple:
    # dominant_style: Optional[str] = None
    # tone: Optional[str] = None
    # suggestions: List[str] = []
    raw_response: Optional[str] = None

class ContentAnalysisRequest(BaseModel):
    text_to_analyze: str
    # chapter_context: Optional[str] = None # Contexte du chapitre si différent du texte analysé

class CharacterContext(BaseModel):
    name: str
    description: Optional[str] = None
    # Ajoutez d'autres champs pertinents pour le contexte du personnage si nécessaire

class GenerationRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    style: Optional[str] = None # Style d'écriture souhaité
    prompt: str # Le prompt principal pour la génération
    action: str # Action spécifique (ex: "continue", "reformulate", "generer_scene")
    
    # Champs optionnels pour différentes actions et contextes
    current_text: Optional[str] = None # Texte actuel de l'éditeur (peut être utilisé pour "continue", "reformulate")
    custom_style_description: Optional[str] = None # Description de style personnalisée si 'style' est 'custom'
    
    # Contexte pour la génération de scène ou actions liées aux personnages
    character_context: Optional[List[CharacterContext]] = None 
    scene_goal: Optional[str] = None # Objectif de la scène à générer
    characters: Optional[List[str]] = None # Noms ou IDs des personnages impliqués dans la scène
    key_elements: Optional[str] = None # Éléments clés à inclure dans la scène
    
    # Contexte plus large
    plot_context: Optional[str] = None # Contexte de l'intrigue
    previous_summary: Optional[str] = None # Résumé du chapitre/scène précédent

class GenerationResponse(BaseModel):
    generated_text: str
    raw_response: Optional[str] = None

# --- Schémas pour l'analyse de cohérence et de chapitre ---
class EntityInfo(BaseModel):
    text: str
    label: str
    count: int

class ConsistencyAnalysisResponse(BaseModel):
    project_id: int
    total_chapters: int
    total_words: int
    entities: List[EntityInfo] = []
    warnings: List[str] = []

class Suggestion(BaseModel):
    original_text: str
    suggested_text: str
    start_index: int
    end_index: int
    comment: Optional[str] = None

class ChapterAnalysisStats(BaseModel):
    word_count: int
    # sentence_count: Optional[int] = None
    # average_sentence_length: Optional[float] = None
    # flesch_reading_ease: Optional[float] = None # Exemple de métrique

class ChapterAnalysisResponse(BaseModel):
    chapter_id: int
    stats: ChapterAnalysisStats
    suggestions: List[Suggestion] = []
    raw_response: Optional[str] = None # Réponse brute de l'IA si utile


# --- Modèles SQLAlchemy ---

# Table d'association pour la relation Many-to-Many entre Scene et Character
scene_character_association = Table(
    'scene_character_association', Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)

    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan", order_by="Chapter.order") # Ajout order_by

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    pov_character_id = Column(Integer, ForeignKey("characters.id"), nullable=True) # NOUVEAU
    order = Column(Integer, default=0)  # NOUVEAU: Ordre du chapitre
    summary = Column(Text, nullable=True) # NOUVEAU: Résumé du chapitre

    project = relationship("Project", back_populates="chapters")
    pov_character = relationship("Character", foreign_keys=[pov_character_id]) # NOUVEAU
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan", order_by="Scene.order") # Ajout order_by

# NOUVEAU: Modèle SQLAlchemy pour Scene
class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)
    order = Column(Integer, default=0) # Ordre de la scène dans le chapitre
    chapter_id = Column(Integer, ForeignKey("chapters.id"))

    chapter = relationship("Chapter", back_populates="scenes")
    # Relation Many-to-Many avec Character
    characters = relationship("Character", secondary=scene_character_association, back_populates="scenes")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    backstory = Column(Text, nullable=True)
    # project_id = Column(Integer, ForeignKey("projects.id")) # Un personnage peut appartenir à un projet

    # project = relationship("Project") # Relation avec Project
    # Relation Many-to-Many avec Scene
    scenes = relationship("Scene", secondary=scene_character_association, back_populates="characters")


# NOUVEAU: Modèle SQLAlchemy pour les Clés API
class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, unique=True, index=True, nullable=False) # ex: "gemini", "mistral"
    encrypted_api_key = Column(String, nullable=False) # Clé API chiffrée
    # iv = Column(String, nullable=False) # Vecteur d'initialisation pour le chiffrement (si AES en mode CBC/CTR etc.)
    # salt = Column(String, nullable=False) # Sel pour la dérivation de clé (si KDF est utilisé)
    # Pour Fernet, le token contient tout


# Appel pour reconstruire les modèles Pydantic qui ont des références forward
# Cela doit être fait après que toutes les classes référencées soient définies.
CharacterRead.model_rebuild()
SceneRead.model_rebuild()
ChapterReadBasic.model_rebuild()
ProjectRead.model_rebuild()
ChapterRead.model_rebuild()
# Ajoutez d'autres modèles qui utilisent des forward references si nécessaire