from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import logging # Importer logging
import re # Importer regex pour parser le nom
from pydantic import BaseModel # Assurez-vous que BaseModel est importé si nécessaire

# Importer les modèles SQLAlchemy et les schémas Pydantic
# Accès aux modèles SQLAlchemy (Character) et schémas Pydantic (CharacterRead, CharacterCreate, etc.)
from backend import models
from backend.database import get_db # Fonction pour obtenir la session DB
# Importer la factory IA et la configuration pour les clés API
from backend.ai_services.factory import create_adapter # Correction: Importer create_adapter
from backend.config import Settings, get_settings # Importer Settings et get_settings

router = APIRouter(
    prefix="/api/characters", # Préfixe pour toutes les routes de ce routeur
    tags=["characters"], # Tag pour la documentation Swagger/OpenAPI
    responses={404: {"description": "Not found"}}, # Réponse par défaut pour les 404
)

# --- Endpoints CRUD pour les Personnages ---

# Endpoint pour créer un nouveau personnage (POST /api/characters)
@router.post("/", response_model=models.CharacterRead, status_code=status.HTTP_201_CREATED)
async def create_character(character: models.CharacterCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau personnage dans la base de données.
    """
    # Convertit le schéma Pydantic en dictionnaire et crée une instance SQLAlchemy
    db_character = models.Character(**character.model_dump()) # Utiliser model_dump() pour Pydantic v2+
    db.add(db_character)
    db.commit()
    db.refresh(db_character) # Rafraîchit l'instance pour obtenir l'ID généré par la DB
    return db_character

# Endpoint pour lister tous les personnages (GET /api/characters)
@router.get("/", response_model=List[models.CharacterRead])
async def read_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Récupère une liste de personnages depuis la base de données avec pagination.
    """
    characters = db.query(models.Character).offset(skip).limit(limit).all()
    return characters

# Endpoint pour récupérer un personnage spécifique par ID (GET /api/characters/{character_id})
@router.get("/{character_id}", response_model=models.CharacterRead)
async def read_character(character_id: int, db: Session = Depends(get_db)):
    """
    Récupère un personnage spécifique par son ID.
    """
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        # Utiliser le status code 404 défini dans les réponses par défaut du routeur
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return db_character

# Endpoint pour mettre à jour un personnage (PUT /api/characters/{character_id})
@router.put("/{character_id}", response_model=models.CharacterRead)
async def update_character(character_id: int, character_update: models.CharacterUpdate, db: Session = Depends(get_db)):
    """
    Met à jour un personnage existant dans la base de données.
    Seuls les champs fournis dans la requête sont mis à jour.
    """
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    # Récupère les données à mettre à jour, en excluant les champs non définis dans la requête
    update_data = character_update.model_dump(exclude_unset=True)

    # Met à jour les attributs du modèle SQLAlchemy
    for key, value in update_data.items():
        setattr(db_character, key, value)

    db.commit()
    db.refresh(db_character)
    return db_character

# Endpoint pour supprimer un personnage (DELETE /api/characters/{character_id})
@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """
    Supprime un personnage de la base de données par son ID.
    """
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    db.delete(db_character)
    db.commit()
    # Pas besoin de retourner de contenu pour une réponse 204
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- NOUVEL Endpoint pour la génération de personnage par IA ---
@router.post("/generate", response_model=models.CharacterGenerateResponse, status_code=status.HTTP_200_OK)
async def generate_character(request: models.CharacterGenerateRequest, settings: Settings = Depends(get_settings)):
    """
    Génère une ébauche de personnage (nom, description, backstory) en utilisant un service IA,
    en tenant compte des caractéristiques optionnelles fournies.
    """
    logging.info(f"Received character generation request: {request}")

    # Construire le prompt pour l'IA
    prompt_base = "Génère une fiche de personnage pour une histoire. Inclus un nom plausible, une courte description physique et psychologique, et une ébauche de backstory (quelques phrases)."

    # Ajouter les caractéristiques optionnelles au prompt si elles sont fournies
    characteristics = []
    if request.ethnicity:
        characteristics.append(f"Ethnie : {request.ethnicity}")
    if request.gender:
        characteristics.append(f"Sexe : {request.gender}")
    if request.approx_age:
        characteristics.append(f"Âge approximatif : {request.approx_age}")
    if request.nationality:
        characteristics.append(f"Nationalité : {request.nationality}")
    if request.job: # NOUVEAU
        characteristics.append(f"Métier : {request.job}")
    if request.clothing: # NOUVEAU
        characteristics.append(f"Vêtements : {request.clothing}")

    if characteristics:
        prompt_base += "\n\nCaractéristiques souhaitées :"
        for char in characteristics:
            prompt_base += f"\n- {char}"

    if request.prompt_details:
        prompt_base += f"\n\nAutres indications de l'utilisateur : \"{request.prompt_details}\""

    # Ajouter une instruction pour faciliter le parsing (optionnel, dépend de la robustesse du parsing)
    prompt_base += "\n\nFormat attendu (approximatif) :\nNom: [Nom du personnage]\nDescription: [Description...]\nBackstory: [Backstory...]"

    # --- Correction: Récupérer la clé API basée sur le provider ---
    api_key = None
    if request.provider == "gemini":
        api_key = settings.gemini_api_key
    elif request.provider == "mistral":
        api_key = settings.mistral_api_key
    elif request.provider == "openrouter":
        api_key = settings.openrouter_api_key
    # Ajoutez d'autres providers ici si nécessaire

    if not api_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"API key for provider '{request.provider}' not configured or provider not supported.")
    # --- Fin Correction ---

    try:
        # Obtenir le service IA via la factory
        ai_service = create_adapter(request.provider, api_key, request.model) # Correction: Utiliser create_adapter

        # Définir l'action spécifique pour les adaptateurs
        action = "generer_personnage"

        # Appeler la méthode generate de l'adaptateur avec le prompt enrichi
        logging.info(f"Calling AI service '{request.provider}' (model: {request.model or 'default'}) with action '{action}' and style '{request.style or 'normal'}'")
        logging.debug(f"Prompt sent to AI: {prompt_base}") # Log le prompt complet pour debug
        raw_response = await ai_service.generate( # AJOUT DE 'await' ICI
            prompt=prompt_base, # Utiliser le prompt enrichi
            action=action,
            style=request.style
            # NOTE: Pour l'instant, on passe les caractéristiques via le prompt.
            # Une évolution pourrait être de les passer comme arguments séparés si les adaptateurs le supportent.
        )
        logging.info(f"Raw response from AI: {raw_response}")

        # --- Parsing basique de la réponse ---
        # C'est une partie simpliste et qui pourrait nécessiter des ajustements
        # en fonction de la variabilité des réponses de l'IA.
        parsed_name = "Personnage Généré" # Défaut
        parsed_description = None
        parsed_backstory = None

        # Essayer d'extraire le nom
        name_match = re.search(r"Nom:\s*(.+)", raw_response, re.IGNORECASE)
        if name_match:
            parsed_name = name_match.group(1).strip()

        # Essayer d'extraire la description
        desc_match = re.search(r"Description:\s*([\s\S]+?)(\nBackstory:|\n\n|$)", raw_response, re.IGNORECASE)
        if desc_match:
            parsed_description = desc_match.group(1).strip()

        # Essayer d'extraire la backstory
        backstory_match = re.search(r"Backstory:\s*([\s\S]+)", raw_response, re.IGNORECASE)
        if backstory_match:
            parsed_backstory = backstory_match.group(1).strip()

        # Si la description ou backstory n'a pas été trouvée avec les marqueurs,
        # on peut essayer de prendre le reste de la réponse comme description/backstory combinées.
        if parsed_description is None and parsed_backstory is None and isinstance(raw_response, str) and len(raw_response) > len(parsed_name):
             # Prendre le reste après le nom (ou toute la réponse si le nom n'est pas trouvé)
             start_index = raw_response.find(parsed_name) + len(parsed_name) if name_match else 0
             remaining_text = raw_response[start_index:].strip().lstrip(':').strip()
             if remaining_text:
                 parsed_description = remaining_text # Mettre tout dans la description par défaut

        # Retourner la réponse structurée
        return models.CharacterGenerateResponse(
            name=parsed_name,
            description=parsed_description,
            backstory=parsed_backstory,
            raw_response=raw_response
        )

    except ValueError as ve:
        logging.error(f"Value error during character generation: {ve}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logging.error(f"Unexpected error during character generation: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne du serveur lors de la génération du personnage: {str(e)}")


# --- Endpoints pour gérer les relations (Optionnel) ---
# Ex: Ajouter un personnage à un projet
# @router.post("/{character_id}/projects/{project_id}", status_code=status.HTTP_200_OK)
# async def add_character_to_project(character_id: int, project_id: int, db: Session = Depends(get_db)):
#     # Logique pour ajouter l'association dans la table project_characters
#     raise HTTPException(status_code=501, detail="Adding character to project not implemented yet.")