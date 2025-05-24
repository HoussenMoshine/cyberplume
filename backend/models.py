from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column # Ajout Mapped, mapped_column pour syntaxe moderne optionnelle
from sqlalchemy.sql import func # Pour default=func.now() si besoin
from pydantic import BaseModel, Field # Ajout Field
from typing import List, Optional # Assurer que List est importé

# Importer Base depuis database.py
from .database import Base

# --- Forward declaration pour les types dans les schémas ---
# Nécessaire car SceneRead utilise CharacterRead et vice-versa (potentiellement)
class CharacterRead(BaseModel):
    pass
class SceneRead(BaseModel):
    pass

# --- Schémas Pydantic pour la création ---

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ChapterBase(BaseModel):
    title: str
    content: Optional[str] = None
    pov_character_id: Optional[int] = None
    order: Optional[int] = None # NOUVEAU: Ordre du chapitre dans le projet

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
class CharacterRead(CharacterBase):
    id: int
    # scene_ids: List[int] = [] # Option 1: Juste les IDs
    scenes: List[SceneRead] = [] # Option 2: Les objets SceneRead complets (attention aux refs circulaires si SceneRead inclut CharacterRead)
                                 # Pour l'instant, on va garder les objets complets, mais on pourrait simplifier si besoin

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
class SceneRead(SceneBase):
    id: int
    chapter_id: int
    characters: List[CharacterRead] = [] # Liste des personnages liés

    class Config:
        from_attributes = True


class ChapterReadBasic(BaseModel): # Utilisé dans ProjectRead
    id: int
    title: str
    project_id: int
    order: int # NOUVEAU: Inclure l'ordre
    # Optionnel: Ajouter les scènes ici si nécessaire dans la vue projet
    # scenes: List[SceneRead] = []

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

# --- Modèles SQLAlchemy ---

# NOUVEAU: Table d'association Scene <-> Character
scene_characters = Table(
    'scene_characters',
    Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Relations définies plus bas

class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0) # NOUVEAU: Ordre dans le projet
    project_id = Column(Integer, ForeignKey('projects.id'))
    pov_character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)

    project = relationship("Project", back_populates="chapters")
    pov_character = relationship("Character", back_populates="chapters_pov") # Renommé back_populates

    # Relation vers les scènes
    scenes = relationship(
        "Scene",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Scene.order" # Ordonner par le champ 'order' (déjà présent)
    )

# Modèle SQLAlchemy pour Scene
class Scene(Base):
    __tablename__ = 'scenes'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False) # Titre un peu plus long ?
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0) # Ordre dans le chapitre, non nullable avec défaut
    chapter_id = Column(Integer, ForeignKey('chapters.id'))

    chapter = relationship("Chapter", back_populates="scenes")

    # NOUVEAU: Relation many-to-many vers les personnages
    characters = relationship(
        "Character",
        secondary=scene_characters,
        back_populates="scenes"
    )


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    backstory = Column(Text, nullable=True)

    # Relations
    chapters_pov = relationship('Chapter', back_populates='pov_character') # Renommé back_populates
    # Relation many-to-many avec Project définie plus bas
    # NOUVEAU: Relation many-to-many vers les scènes
    scenes = relationship(
        "Scene",
        secondary=scene_characters,
        back_populates="characters"
    )

# NOUVEAU: Modèle SQLAlchemy pour les Clés API
class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False, index=True)
    encrypted_api_key = Column(String(512), nullable=False) # Assez long pour une clé chiffrée avec Fernet

# Table d'association pour la relation many-to-many Project <-> Character
project_characters = Table(
    'project_characters',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

# Définir les relations après la définition de toutes les classes et tables
Project.chapters = relationship(
    'Chapter',
    back_populates='project',
    cascade="all, delete-orphan",
    order_by='Chapter.order' # MODIFIÉ: Trier par le nouveau champ 'order'
)
Project.characters = relationship('Character', secondary=project_characters, back_populates='projects', cascade="all, delete")
Character.projects = relationship('Project', secondary=project_characters, back_populates='characters')


# --- Schéma pour le contexte personnage ---
# NOUVEAU: Schéma pour passer les infos personnages à l'IA
class CharacterContext(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    backstory: Optional[str] = None

# --- Autres Schémas ---

# MODIFIÉ: Ajout des champs optionnels pour la génération de scène, style personnalisé ET contexte personnages
class GenerationRequest(BaseModel):
    provider: str
    prompt: str # Description générale ou contexte
    model: Optional[str] = None
    action: Optional[str] = None # Ex: 'continue', 'suggest', 'dialogue', 'generate_scene'
    style: Optional[str] = None
    # Champs pour enrichir la génération de scène (utilisés par action='generate_scene')
    characters: Optional[List[str]] = Field(None, description="Noms des personnages présents dans la scène")
    scene_goal: Optional[str] = Field(None, description="Objectif principal de la scène")
    key_elements: Optional[str] = Field(None, description="Éléments ou détails clés à inclure dans la scène")
    # Champ pour le style personnalisé analysé
    custom_style_description: Optional[str] = Field(None, description="Description du style personnalisé analysé à utiliser à la place du style standard")
    # NOUVEAU: Champ pour le contexte des personnages pertinents (utilisé par 'continue', 'suggest', 'dialogue')
    character_context: Optional[List[CharacterContext]] = Field(None, description="Informations sur les personnages pertinents pour le contexte actuel")


class ConsistencyAnalysisRequest(BaseModel):
    project_id: int

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

# --- NOUVEAU: Schémas pour l'analyse de contenu de chapitre ---

class Suggestion(BaseModel):
    """Représente une suggestion d'amélioration pour une partie du texte."""
    original_text: str = Field(..., description="Le segment de texte original concerné.")
    suggested_text: str = Field(..., description="Le texte suggéré en remplacement.")
    suggestion_type: str = Field(..., description="Type de suggestion (ex: 'orthographe', 'grammaire', 'style', 'répétition', 'clarté', 'rythme').")
    explanation: Optional[str] = Field(None, description="Explication facultative de la suggestion.")
    # AJOUT: Indices de début et de fin pour l'application dans l'éditeur
    start_index: int = Field(..., description="Index de début (basé sur 0) du segment original_text dans le contenu complet.")
    end_index: int = Field(..., description="Index de fin (exclusif, basé sur 0) du segment original_text dans le contenu complet.")


class ChapterAnalysisStats(BaseModel):
    """Statistiques calculées sur le contenu du chapitre."""
    word_count: int = Field(..., description="Nombre total de mots dans le chapitre.")
    character_count: Optional[int] = Field(None, description="Nombre total de caractères.")
    sentence_count: Optional[int] = Field(None, description="Nombre total de phrases.")
    readability_score: Optional[float] = Field(None, description="Score de lisibilité (ex: Flesch-Kincaid).")
    estimated_reading_time_minutes: Optional[float] = Field(None, description="Temps de lecture estimé en minutes.")

class ChapterAnalysisResponse(BaseModel):
    """Réponse de l'API d'analyse de contenu de chapitre."""
    chapter_id: int
    stats: ChapterAnalysisStats
    suggestions: List[Suggestion] = []


# --- Résolution des forward references pour Pydantic ---
# Nécessaire si les schémas s'utilisent mutuellement avant d'être complètement définis
CharacterRead.model_rebuild()
SceneRead.model_rebuild()