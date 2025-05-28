# backend/routers/scenes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload # Ajout selectinload
from typing import List
# from pydantic import BaseModel # Plus nécessaire ici

from ..database import get_db
from .. import models # CORRECTION: Importer uniquement models
# NOUVEAU: Importer le schéma de réordonnancement depuis models
from ..models import ReorderItemsSchema


router = APIRouter(
    # prefix="/api", # Préfixe commun -- Supprimé car géré par le proxy Vite
    tags=["Scenes"],
    responses={404: {"description": "Not found"}},
)

# --- Helpers ---

def get_chapter_or_404(chapter_id: int, db: Session) -> models.Chapter:
    """Récupère un chapitre par ID ou lève une exception 404."""
    # Charger les scènes en même temps pour éviter des requêtes N+1 potentielles
    # Utiliser selectinload pour les scènes ici aussi peut être bénéfique si on accède souvent aux scènes après avoir chargé le chapitre
    chapter = db.query(models.Chapter).options(selectinload(models.Chapter.scenes)).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found",
        )
    return chapter

def get_scene_or_404(scene_id: int, db: Session, load_characters: bool = False) -> models.Scene:
    """Récupère une scène par ID ou lève une exception 404.
       Charge optionnellement les personnages liés.
    """
    query = db.query(models.Scene)
    if load_characters:
        # Utiliser selectinload pour charger les personnages efficacement
        query = query.options(selectinload(models.Scene.characters))
    scene = query.filter(models.Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene with id {scene_id} not found",
        )
    return scene

# NOUVEAU: Helper pour récupérer un personnage
def get_character_or_404(character_id: int, db: Session) -> models.Character:
    """Récupère un personnage par ID ou lève une exception 404."""
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )
    return character


# --- Routes CRUD pour les Scènes ---

@router.post("/chapters/{chapter_id}/scenes/", response_model=models.SceneRead, status_code=status.HTTP_201_CREATED)
def create_scene_for_chapter(
    chapter_id: int,
    scene: models.SceneCreate,
    db: Session = Depends(get_db)
):
    """Crée une nouvelle scène pour un chapitre spécifique.
       L'ordre est automatiquement défini à la fin.
    """
    db_chapter = get_chapter_or_404(chapter_id, db)

    # Déterminer l'ordre de la nouvelle scène (à la fin par défaut)
    # Re-requêter pour être sûr d'avoir le compte le plus à jour si beaucoup d'ajouts concurrents (peu probable ici)
    # ou utiliser len(db_chapter.scenes) si le selectinload est fiable
    last_scene = db.query(models.Scene).filter(models.Scene.chapter_id == chapter_id).order_by(models.Scene.order.desc()).first()
    next_order = (last_scene.order + 1) if last_scene else 0

    # CORRECTION: Exclure 'order' du dump avant de dépaqueter, puis l'ajouter explicitement
    scene_data = scene.model_dump(exclude={'order'}) # Exclure 'order'

    db_scene = models.Scene(
        **scene_data, # Dépaqueter les données sans 'order'
        chapter_id=chapter_id,
        order=next_order # Ajouter l'ordre explicitement
    )
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    # Recharger la scène avec les personnages pour la réponse (même si vide au début)
    db_scene_with_chars = get_scene_or_404(db_scene.id, db, load_characters=True)
    return db_scene_with_chars

@router.get("/chapters/{chapter_id}/scenes/", response_model=List[models.SceneRead])
def read_scenes_for_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Récupère toutes les scènes d'un chapitre spécifique, ordonnées et avec leurs personnages."""
    db_chapter = get_chapter_or_404(chapter_id, db) # Vérifie que le chapitre existe
    # Charger explicitement les personnages pour chaque scène
    # Utiliser une requête séparée pour charger les scènes avec les personnages
    scenes = db.query(models.Scene).options(
        selectinload(models.Scene.characters) # Charger les personnages liés
    ).filter(models.Scene.chapter_id == chapter_id).order_by(models.Scene.order).all()
    return scenes

@router.get("/scenes/{scene_id}", response_model=models.SceneRead)
def read_scene(scene_id: int, db: Session = Depends(get_db)):
    """Récupère les détails d'une scène spécifique, incluant les personnages liés."""
    # Charger la scène avec les personnages
    db_scene = get_scene_or_404(scene_id, db, load_characters=True)
    return db_scene

@router.put("/scenes/{scene_id}", response_model=models.SceneRead)
def update_scene(
    scene_id: int,
    scene_update: models.SceneUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une scène spécifique (titre, contenu, ordre).
       Ne modifie pas les personnages liés via cette route.
       ATTENTION: La mise à jour de l'ordre ici peut désynchroniser l'ordre global.
                 Préférez utiliser la route /reorder pour les changements d'ordre.
    """
    db_scene = get_scene_or_404(scene_id, db, load_characters=True) # Charger les personnages pour la réponse

    update_data = scene_update.model_dump(exclude_unset=True) # Ne met à jour que les champs fournis

    for key, value in update_data.items():
        setattr(db_scene, key, value)

    db.commit()
    db.refresh(db_scene)
    # Recharger explicitement les personnages après refresh si nécessaire (normalement pas besoin avec selectinload avant commit)
    # db.refresh(db_scene, attribute_names=['characters'])
    return db_scene

@router.delete("/scenes/{scene_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scene(scene_id: int, db: Session = Depends(get_db)):
    """Supprime une scène spécifique."""
    db_scene = get_scene_or_404(scene_id, db)
    # La suppression en cascade devrait gérer la table d'association scene_characters
    db.delete(db_scene)
    db.commit()
    # Pas de contenu à retourner pour une suppression réussie
    return None

# --- NOUVEAU: Routes pour lier/délier les personnages aux scènes ---

@router.post("/scenes/{scene_id}/characters/{character_id}", response_model=models.SceneRead, status_code=status.HTTP_200_OK)
def link_character_to_scene(
    scene_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Associe un personnage existant à une scène existante."""
    db_scene = get_scene_or_404(scene_id, db, load_characters=True)
    db_character = get_character_or_404(character_id, db)

    if db_character in db_scene.characters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character already linked to this scene",
        )

    db_scene.characters.append(db_character)
    db.commit()
    db.refresh(db_scene)
    # Recharger pour être sûr que la liste est à jour dans la réponse
    db.refresh(db_scene, attribute_names=['characters'])
    return db_scene

@router.delete("/scenes/{scene_id}/characters/{character_id}", response_model=models.SceneRead, status_code=status.HTTP_200_OK)
def unlink_character_from_scene(
    scene_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Dissocie un personnage d'une scène."""
    db_scene = get_scene_or_404(scene_id, db, load_characters=True)
    db_character = get_character_or_404(character_id, db)

    if db_character not in db_scene.characters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Ou 400 Bad Request ? 404 semble ok
            detail="Character not linked to this scene",
        )

    db_scene.characters.remove(db_character)
    db.commit()
    db.refresh(db_scene)
    # Recharger pour être sûr que la liste est à jour dans la réponse
    db.refresh(db_scene, attribute_names=['characters'])
    return db_scene


# NOUVELLE ROUTE: Réordonner les scènes d'un chapitre
@router.post("/chapters/{chapter_id}/scenes/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_chapter_scenes(chapter_id: int, reorder_data: ReorderItemsSchema, db: Session = Depends(get_db)):
    """
    Met à jour l'ordre des scènes pour un chapitre donné.
    La liste `ordered_ids` doit contenir tous les IDs des scènes du chapitre,
    dans le nouvel ordre souhaité.
    """
    # Vérifier si le chapitre existe
    db_chapter = get_chapter_or_404(chapter_id, db) # Utilise le helper qui charge déjà les scènes

    ordered_ids = reorder_data.ordered_ids
    # Récupérer toutes les scènes actuelles du chapitre (déjà chargées par get_chapter_or_404 via selectinload)
    # ou requêter à nouveau si on n'est pas sûr :
    scenes = db.query(models.Scene).filter(models.Scene.chapter_id == chapter_id).all()
    scene_map = {scene.id: scene for scene in scenes}

    # Vérifier si tous les IDs fournis correspondent aux scènes du chapitre
    if set(ordered_ids) != set(scene_map.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided IDs do not match the scenes of the chapter. Ensure all scene IDs for the chapter are included exactly once."
        )

    # Mettre à jour l'ordre
    for index, scene_id in enumerate(ordered_ids):
        scene = scene_map.get(scene_id)
        if scene: # Sécurité
            scene.order = index # Assigner le nouvel index comme ordre

    db.commit()
    return None # Pas de contenu à retourner pour 204