from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Set
import logging
# from pydantic import BaseModel # Plus nécessaire ici si ReorderItemsSchema est le seul schéma local

# Importer les modèles SQLAlchemy, les schémas Pydantic et la dépendance get_db
from .. import models # Utiliser .. pour remonter d'un niveau
from ..database import get_db # Importer la fonction get_db depuis database.py
# NOUVEAU: Importer le schéma de réordonnancement depuis models
from ..models import ReorderItemsSchema
# NOUVEAU: Importer le service de résumé
from ..services import summary_service


router = APIRouter(
    # prefix="/api", # Préfixe commun pour ces routes -- Supprimé car géré par le proxy Vite
    tags=["Projects & Chapters"], # Tag pour la documentation Swagger UI
)

# --- SUPPRIMÉ: Schéma pour le réordonnancement (maintenant dans models.py) ---
# class ReorderItemsSchema(BaseModel):
#     ordered_ids: List[int]

# --- Endpoints pour les Projets ---

@router.post("/projects", response_model=models.ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(project: models.ProjectCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau projet.
    """
    db_project = models.Project(**project.model_dump()) # Utiliser model_dump pour Pydantic v2+
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=List[models.ProjectRead])
async def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Récupère une liste de projets avec pagination.
    Inclut les informations de base des chapitres associés, triés par leur ordre.
    """
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    # Le tri est géré par la relation `order_by='Chapter.order'` dans models.py
    return projects

@router.get("/projects/{project_id}", response_model=models.ProjectRead)
async def read_project(project_id: int, db: Session = Depends(get_db)):
    """
    Récupère un projet spécifique par son ID, incluant les informations
    de base de ses chapitres, triés par leur ordre.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    # Le tri est géré par la relation `order_by='Chapter.order'` dans models.py
    return db_project

@router.put("/projects/{project_id}", response_model=models.ProjectRead)
async def update_project(project_id: int, project_update: models.ProjectUpdate, db: Session = Depends(get_db)): # Utiliser ProjectUpdate
    """
    Met à jour un projet existant.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Mettre à jour les champs fournis
    update_data = project_update.model_dump(exclude_unset=True) # Utiliser model_dump pour Pydantic v2+
    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.add(db_project) # Ajoute l'objet modifié à la session
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Supprime un projet et potentiellement ses chapitres associés (selon la configuration de la relation).
    """
    print(f"[ROUTER] Attempting to delete project with ID: {project_id}")
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Assumant que la cascade delete est configurée dans models.py pour les chapitres
    db.delete(db_project)
    db.commit()
    return None


@router.delete("/projects/batch", status_code=status.HTTP_204_NO_CONTENT)
async def delete_projects_batch(batch_data: models.DeleteBatchSchema, db: Session = Depends(get_db)):
    """
    Supprime plusieurs projets et leurs chapitres associés en une seule fois.
    """
    projects_to_delete = db.query(models.Project).filter(models.Project.id.in_(batch_data.ids)).all()

    if not projects_to_delete:
        return None

    # Optionnel: Logguer si certains IDs n'ont pas été trouvés
    if len(projects_to_delete) != len(set(batch_data.ids)):
        found_ids = {p.id for p in projects_to_delete}
        not_found_ids = [id for id in set(batch_data.ids) if id not in found_ids]
        print(f"Warning: Projects with IDs {not_found_ids} not found for batch delete.") # Remplacer par logger

    for project in projects_to_delete:
        db.delete(project) # Assumant cascade delete

    db.commit()
    return None


# --- Endpoints pour les Chapitres ---

# Correction: Imbriquer la route sous /projects/{project_id}/chapters
@router.post("/projects/{project_id}/chapters", response_model=models.ChapterRead, status_code=status.HTTP_201_CREATED)
async def create_chapter_for_project(project_id: int, chapter_data: models.ChapterCreateNoProjectId, db: Session = Depends(get_db)): # Utiliser project_id de l'URL
    """
    Crée un nouveau chapitre associé à un projet existant (identifié par l'URL).
    L'ordre initial sera déterminé automatiquement (ajout à la fin).
    """
    # Vérifier si le projet parent existe
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Vérifier si le personnage POV existe (si fourni)
    if chapter_data.pov_character_id:
        db_character = db.query(models.Character).filter(models.Character.id == chapter_data.pov_character_id).first()
        if db_character is None:
             raise HTTPException(status_code=404, detail=f"Character with id {chapter_data.pov_character_id} not found")

    # Déterminer le prochain ordre
    last_chapter = db.query(models.Chapter).filter(models.Chapter.project_id == project_id).order_by(models.Chapter.order.desc()).first()
    next_order = (last_chapter.order + 1) if last_chapter else 0

    # Créer l'objet Chapter en ajoutant project_id et order
    chapter_dict = chapter_data.model_dump()
    chapter_dict.pop('order', None) # Retirer l'ordre du payload s'il est présent
    db_chapter = models.Chapter(**chapter_dict, project_id=project_id, order=next_order)
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@router.get("/projects/{project_id}/chapters", response_model=List[models.ChapterReadBasic])
async def read_project_chapters(project_id: int, db: Session = Depends(get_db)):
    """
    Récupère la liste des chapitres (informations de base) pour un projet donné,
    triés par leur ordre.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Le tri est géré par la relation `order_by='Chapter.order'` dans models.py
    # Si ce n'est pas le cas ou pour être explicite :
    chapters = db.query(models.Chapter).filter(models.Chapter.project_id == project_id).order_by(models.Chapter.order).all()
    return chapters

@router.get("/chapters/{chapter_id}", response_model=models.ChapterRead)
async def read_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """
    Récupère un chapitre spécifique par son ID, incluant son contenu et ses scènes (triées).
    """
    db_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if db_chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    # Le tri des scènes est géré par la relation `order_by='Scene.order'` dans models.py
    return db_chapter

# Correction: Utiliser ChapterUpdate pour la mise à jour partielle
@router.put("/chapters/{chapter_id}", response_model=models.ChapterRead)
async def update_chapter(chapter_id: int, chapter_update: models.ChapterUpdate, db: Session = Depends(get_db)):
    """
    Met à jour un chapitre existant (titre, contenu, personnage POV, ordre).
    Ne permet pas de changer le projet associé.
    ATTENTION: La mise à jour de l'ordre ici peut désynchroniser l'ordre global.
              Préférez utiliser la route /reorder pour les changements d'ordre.
    """
    db_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if db_chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Vérifier si le nouveau personnage POV existe (si fourni et différent)
    # Utiliser getattr pour vérifier si pov_character_id est dans l'update
    new_pov_id = getattr(chapter_update, 'pov_character_id', None)
    if new_pov_id is not None and new_pov_id != db_chapter.pov_character_id:
        db_character = db.query(models.Character).filter(models.Character.id == new_pov_id).first()
        if db_character is None:
             raise HTTPException(status_code=404, detail=f"Character with id {new_pov_id} not found")

    # Mettre à jour les champs fournis
    update_data = chapter_update.model_dump(exclude_unset=True) # Utiliser model_dump et exclude_unset
    for key, value in update_data.items():
        setattr(db_chapter, key, value)

    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """
    Supprime un chapitre spécifique par son ID.
    """
    logging.info(f"Attempting to delete chapter with ID: {chapter_id}")
    try:
        db_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if db_chapter is None:
            logging.warning(f"Chapter with ID {chapter_id} not found for deletion.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

        logging.debug(f"Chapter found: {db_chapter}. Proceeding to delete associated scenes.")
        # Supprimer les scènes associées manuellement
        num_deleted_scenes = db.query(models.Scene).filter(models.Scene.chapter_id == chapter_id).delete(synchronize_session='evaluate') # Modifié synchronize_session
        logging.info(f"Deleted {num_deleted_scenes} scenes associated with chapter ID {chapter_id}.")

        logging.debug(f"Deleting chapter object ID {chapter_id} itself.")
        db.delete(db_chapter)
        
        logging.info(f"Committing changes to the database for chapter ID {chapter_id} deletion.")
        db.commit()
        logging.info(f"Successfully deleted chapter with ID: {chapter_id}")
        return None # HTTP 204 ne retourne pas de contenu
    except HTTPException: # Re-lever les HTTPException pour que FastAPI les gère
        raise
    except Exception as e:
        logging.exception(f"An unexpected error occurred while deleting chapter ID {chapter_id}: {e}")
        db.rollback() # Important de rollback en cas d'erreur
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during chapter deletion.")


@router.delete("/chapters/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapters_batch(batch_data: models.DeleteBatchSchema, db: Session = Depends(get_db)):
    """
    Supprime plusieurs chapitres en une seule fois.
    """
    chapters_to_delete = db.query(models.Chapter).filter(models.Chapter.id.in_(batch_data.ids)).all()

    if not chapters_to_delete:
        return None # Ou lever une 404 si aucun ID n'est trouvé ? Pour l'instant, silencieux.

    # Optionnel: Logguer si certains IDs n'ont pas été trouvés
    if len(chapters_to_delete) != len(set(batch_data.ids)):
        found_ids = {c.id for c in chapters_to_delete}
        not_found_ids = [id for id in set(batch_data.ids) if id not in found_ids]
        print(f"Warning: Chapters with IDs {not_found_ids} not found for batch delete.") # Remplacer par logger

    for chapter in chapters_to_delete:
        db.delete(chapter)

    db.commit()
    return None


@router.post("/projects/{project_id}/chapters/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_project_chapters(project_id: int, reorder_data: ReorderItemsSchema, db: Session = Depends(get_db)):
    """
    Réordonne les chapitres d'un projet donné.
    La liste `ordered_ids` doit contenir tous les IDs des chapitres du projet,
    dans le nouvel ordre souhaité.
    """
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")

    # Vérifier que tous les chapitres du projet sont présents dans la liste et vice-versa
    current_chapter_ids = {chapter.id for chapter in db_project.chapters}
    provided_chapter_ids = set(reorder_data.ordered_ids)

    if current_chapter_ids != provided_chapter_ids:
        missing_ids = current_chapter_ids - provided_chapter_ids
        extra_ids = provided_chapter_ids - current_chapter_ids
        detail = "Mismatch in chapter IDs for reordering. "
        if missing_ids:
            detail += f"Missing from payload: {missing_ids}. "
        if extra_ids:
            detail += f"Unknown in project: {extra_ids}."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    # Mettre à jour l'ordre
    for i, chapter_id in enumerate(reorder_data.ordered_ids):
        chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
        if chapter: # Devrait toujours être vrai à cause de la vérification ci-dessus
            chapter.order = i
            db.add(chapter)

    db.commit()
    return None

# --- Endpoint pour la Génération de Résumé de Chapitre ---

@router.post("/chapters/{chapter_id}/generate-summary", response_model=models.ChapterRead, status_code=status.HTTP_200_OK)
async def generate_chapter_summary_route(chapter_id: int, request: models.SummaryGenerateRequest, db: Session = Depends(get_db)):
    """
    Déclenche la génération et la sauvegarde du résumé pour un chapitre spécifique.
    Retourne le chapitre avec son résumé (potentiellement mis à jour).
    """
    db_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if db_chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    try:
        await summary_service.generate_and_save_summary(db_chapter, db, provider=request.provider, model=request.model)
        # Le service s'occupe du db.commit() et db.refresh(db_chapter)
    except HTTPException as e:
        # Propage l'exception HTTP levée par le service (ex: erreur IA, configuration)
        raise e
    except Exception as e:
        # Gérer les autres erreurs inattendues du service
        print(f"Erreur inattendue lors de la génération du résumé pour le chapitre {chapter_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne lors de la génération du résumé: {str(e)}")
    
    # db.refresh(db_chapter) # Normalement fait par le service après commit, ou implicite si la session est la même.
                            # Pour être sûr, on peut le faire ici si le service ne le garantit pas.
                            # Mais si le service fait db.refresh, c'sest bon.
    return db_chapter